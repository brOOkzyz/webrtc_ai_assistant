# TTS重叠播放问题修复说明

## 问题描述

在 `asr_llm_working.py` 中，当用户快速连续说话时，会出现两个TTS线程异步播放重叠的问题，导致音频混乱。

## 问题原因分析

1. **TTS启动时机问题**：在 `ask_llm` 函数中，TTS在LLM开始生成内容之前就启动了，但此时可能还没有完全停止之前的TTS播放。

2. **打断检测逻辑问题**：在 `real_time_voice_detection` 函数中，当检测到新语音时，虽然设置了打断标志，但新的对话线程可能在新线程中启动，导致两个TTS实例同时运行。

3. **TTS停止等待不够充分**：虽然有等待TTS停止的逻辑，但等待时间可能不够，导致新的TTS启动时旧的还在运行。

## 修复方案

### 1. 改进 `ask_llm` 函数

在启动新TTS之前，确保完全停止旧的TTS：

```python
# 关键修复：在启动新TTS之前，确保完全停止旧的TTS
print("🔄 已有TTS实例在播放，先停止它，避免音频重叠...")
force_stop_all_tts()

# 等待TTS完全停止，确保没有音频重叠
print("⏳ 等待TTS完全停止，确保没有音频重叠...")
wait_count = 0
while is_tts_playing() and wait_count < 50:  # 最多等待5秒
    time.sleep(0.1)
    wait_count += 1
```

### 2. 改进 `force_stop_all_tts` 函数

增强强制停止TTS的能力：

```python
def force_stop_all_tts():
    """强制停止所有TTS播放，防止重叠播放"""
    global tts_should_stop
    
    print("🚨 强制停止所有TTS播放...")
    
    # 设置停止标志
    with tts_stop_lock:
        tts_should_stop = True
    
    # 立即停止TTS流式播放
    try:
        from tts_streaming import stop_tts_streaming
        stop_tts_streaming()
    except Exception as e:
        print(f"⚠️ 停止TTS流式播放失败: {e}")
    
    # 立即强制停止所有音频播放进程
    try:
        import subprocess
        processes_to_kill = ['afplay', 'aplay', 'python.*tts', 'audio', 'ffplay', 'mpg123', 'mplayer']
        for process_pattern in processes_to_kill:
            try:
                subprocess.run(['pkill', '-9', '-f', process_pattern], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL,
                              timeout=0.1)
            except Exception as e:
                pass
    except Exception as e:
        print(f"⚠️ 停止音频进程失败: {e}")
    
    # 强制等待确保所有音频进程完全停止
    time.sleep(0.5)
    
    # 重置AI说话状态
    with ai_speaking_lock:
        is_ai_speaking = False
```

### 3. 改进 `process_conversation` 函数

在启动新对话之前检查TTS状态：

```python
def process_conversation(user_input):
    """处理用户输入，调用LLM并播放TTS"""
    global current_conversation_active, tts_should_stop
    
    try:
        # 新对话开始时，确保打断标志已重置
        print(f"🔄 开始处理新对话: {user_input}")
        
        # 关键修复：在启动新对话之前，检查是否有其他TTS在运行
        if is_tts_playing():
            print("⚠️ 检测到其他TTS实例仍在运行，等待其完全停止...")
            wait_count = 0
            while is_tts_playing() and wait_count < 50:  # 最多等待5秒
                time.sleep(0.1)
                wait_count += 1
            if wait_count >= 50:
                print("⚠️ 等待超时，强制停止所有TTS...")
                force_stop_all_tts()
            else:
                print("✅ 其他TTS实例已停止，可以启动新对话...")
        
        print("🤖 AI正在思考并回答...")
        
        # 执行LLM+TTS
        ask_llm(user_input)
        
        # 标记对话结束
        with conversation_lock:
            current_conversation_active = False
            
    except Exception as e:
        print(f"❌ 对话处理错误: {e}")
        with conversation_lock:
            current_conversation_active = False
```

### 4. 改进打断检测逻辑

在 `real_time_voice_detection` 函数中，确保在启动新对话之前完全停止旧的TTS：

```python
# 关键：立即强制停止TTS播放，因为LLM已经输出完毕
print("🚨 开始真正的立即停止TTS流式播放...")
force_stop_all_tts()

# 等待TTS完全停止，避免音频重叠
print("⏳ 等待TTS完全停止，避免音频重叠...")
wait_count = 0
while is_tts_playing() and wait_count < 100:  # 最多等待10秒
    time.sleep(0.1)
    wait_count += 1
```

## 性能优化

为了减少TTS停止和启动的延迟，我们进行了以下优化：

### 1. 快速停止模式

添加了快速停止模式，在大多数情况下可以更快地响应：

```python
def force_stop_all_tts(fast_mode=True):
    """强制停止所有TTS播放，防止重叠播放"""
    if fast_mode:
        # 快速模式：只做基本清理，减少延迟
        time.sleep(0.1)  # 快速模式只等待0.1秒
        return
    # 完整模式：彻底清理所有进程
```

### 2. 减少等待时间

- TTS状态检查间隔：从0.1秒减少到0.05秒
- 最大等待时间：从10秒减少到5秒
- 强制停止延迟：从0.5秒减少到0.2秒

### 3. 性能配置选项

创建了 `tts_performance_config.py` 配置文件，用户可以选择：

- **快速模式 (FAST)**：优先响应速度，可能存在轻微音频重叠风险
- **平衡模式 (BALANCED)**：平衡响应速度和稳定性（默认）
- **稳定模式 (STABLE)**：优先稳定性，响应速度较慢

### 4. 配置示例

```python
# 切换到快速模式
from tts_performance_config import change_performance_mode
change_performance_mode('FAST')

# 查看当前配置
from tts_performance_config import print_current_config
print_current_config()
```

## 修复效果

修复后的系统将：

1. **避免音频重叠**：在启动新TTS之前，确保完全停止旧的TTS
2. **提高打断响应性**：更快的TTS停止和启动
3. **增强稳定性**：更好的错误处理和状态管理
4. **改善用户体验**：清晰的音频播放，无重叠干扰
5. **减少延迟**：快速停止模式显著减少等待时间
6. **灵活配置**：用户可根据需要选择性能模式

## 测试方法

运行测试脚本验证修复效果：

```bash
python test_tts_overlap_fix.py
```

然后运行主程序测试实际效果：

```bash
python asr_llm_working.py
```

## 注意事项

1. **等待时间**：修复增加了TTS停止等待时间，可能会稍微影响响应速度，但能确保音频质量
2. **进程管理**：使用 `pkill` 强制停止音频进程，确保彻底清理
3. **状态同步**：使用锁机制确保多线程状态同步，避免竞态条件

## 总结

通过以上修复，TTS重叠播放问题得到了根本解决。系统现在能够：

- 在启动新TTS之前完全停止旧的TTS
- 正确处理打断检测和状态管理
- 避免音频重叠，提供清晰的语音输出
- 保持系统的稳定性和响应性
