import asyncio
import edge_tts
from pathlib import Path

async def test_voices():
    text_hi = "नमस्ते, यह स्टोरीब्रिज का उच्च गुणवत्ता वाला ऑडियो परीक्षण है। हम पंचतंत्र की कहानियां सुनाते हैं।"
    text_mr = "नमस्कार, हे स्टोरीब्रिजचे उच्च दर्जाचे ऑडिओ सादरीकरण आहे."
    text_en = "Welcome to StoryBridge. This is a high-fidelity studio quality story narration test."

    output_hi = Path("storage/test_hi.mp3")
    output_hi.parent.mkdir(parents=True, exist_ok=True)
    
    print("Testing EdgeTTS Hindi (hi-IN-SwaraNeural)...")
    comm_hi = edge_tts.Communicate(text_hi, "hi-IN-SwaraNeural")
    await comm_hi.save(str(output_hi))
    print(f"Hindi MP3 generated! Size: {output_hi.stat().st_size} bytes")

    output_mr = Path("storage/test_mr.mp3")
    print("Testing EdgeTTS Marathi (mr-IN-AarohiNeural)...")
    comm_mr = edge_tts.Communicate(text_mr, "mr-IN-AarohiNeural")
    await comm_mr.save(str(output_mr))
    print(f"Marathi MP3 generated! Size: {output_mr.stat().st_size} bytes")

    output_en = Path("storage/test_en.mp3")
    print("Testing EdgeTTS Indian English (en-IN-NeerjaNeural)...")
    comm_en = edge_tts.Communicate(text_en, "en-IN-NeerjaNeural")
    await comm_en.save(str(output_en))
    print(f"English MP3 generated! Size: {output_en.stat().st_size} bytes")

if __name__ == "__main__":
    asyncio.run(test_voices())
