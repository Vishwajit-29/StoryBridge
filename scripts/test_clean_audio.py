import asyncio
import edge_tts
from pathlib import Path

async def test_clean_audio():
    # Clean storytelling text with natural punctuation (ellipses, danda, paragraphs)
    text = (
        "पहला अध्याय: दोपहर का विराम।\n\n"
        "एक प्राचीन नगर के बाहर एक भव्य मंदिर का निर्माण कार्य चल रहा था। "
        "वहां अनेक बढ़ई और कारीगर लकड़ी चीरने और तराशने में लगे हुए थे।\n\n"
        "दोपहर के समय जब भोजन का समय हुआ, तो एक कुशल बढ़ई ने एक विशाल लट्ठे को बीच से आधा चीरकर छोड़ दिया। "
        "चीर आपस में चिपक न जाए, इसलिए उसने दोनों भागों के बीच लकड़ी की एक मजबूत कील ठोंक दी... और सभी मजदूर भोजन के लिए चले गए।"
    )

    out = Path("storage/test_clean_swara.mp3")
    comm = edge_tts.Communicate(text=text, voice="hi-IN-SwaraNeural", rate="-4%")
    await comm.save(str(out))
    print(f"Generated clean MP3: {out.stat().st_size} bytes")

if __name__ == "__main__":
    asyncio.run(test_clean_audio())
