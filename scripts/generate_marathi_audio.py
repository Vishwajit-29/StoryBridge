import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ai-engine"))
from providers.tts import EdgeTTSProvider, clean_storytelling_text

MARATHI_SCRIPT = {
    "title": "माकड आणि लाकडी पाचर",
    "synopsis": "पंचतंत्रातील ही प्रसिद्ध बोधप्रद कथा आपल्याला शिकवते की ज्या कामाशी आपला थेट संबंध नाही, त्यात नाहक ढवळाढवळ केल्यास त्याचे भयंकर आणि विनाशकारी परिणाम भोगावे लागतात.",
    "entity_name_map": {
        "Curious Monkey": "खोडकर माकड",
        "Master Carpenter": "कुशल सुतार",
        "Temple Construction Grove": "मंदिर निर्माण परिसर",
        "Wooden Wedge": "लाकडी पाचर"
    },
    "chapters": [
        {
            "chapter_id": "ch_01",
            "chapter_number": 1,
            "title": "पहिला भाग: दुपारची विश्रांती आणि लाकडी पाचर",
            "content": (
                "एका प्राचीन नगराच्या वेशीवर एका भव्य आणि सुंदर मंदिराचे बांधकाम सुरू होते. "
                "तिथे अनेक गवंडी, कारागीर आणि कुशल सुतार लाकूड तासण्यात आणि खांब कोरण्यात मग्न होते.\n\n"
                "दुपारच्या वेळी जेव्हा जेवणाची घंटा वाजली, तेव्हा एका मुख्य सुताराने एका महाकाय लाकडी ओंडक्याला मध्यभागातून अर्धे चिरून ठेवले होते. "
                "तो चिरलेला ओंडका पुन्हा एकमेकांवर आपटून मिटू नये म्हणून त्याने त्या भेगेमध्ये लाकडाची एक भक्कम पाचर ठोकून बसवली... आणि सर्व कामगार जेवणासाठी निघून गेले."
            ),
            "cultural_notes": "पारंपरिक अस्सल मराठी कथाकथन शैली.",
            "word_count": 75,
            "estimated_duration_seconds": 38
        },
        {
            "chapter_id": "ch_02",
            "chapter_number": 2,
            "title": "दुसरा भाग: खोडकर माकडाचे अजब कौतुक",
            "content": (
                "कामगार निघून जाताच झाडांच्या फांद्यांवरून माकडांची एक मोठी टोळी खाली उतरली. "
                "ती माकडे सर्वत्र उड्या मारू लागली आणि कारागिरांच्या साहित्याची नासधूस करू लागली.\n\n"
                "त्या टोळीमध्ये एक अत्यंत खोडकर आणि चंचल माकड होते. त्याचे लक्ष त्या अर्ध्या चिरलेल्या ओंडक्यावर आणि त्यात ठोकलेल्या लाकडी पाचरीवर गेले. "
                "त्या लाकडाचा प्रचंड ताण न समजता, ते माकड त्या भेगेवर दोन्ही पाय पसरून बसले आणि ती पाचर दोन्ही हातांनी जोरजोराने हलवू लागले."
            ),
            "cultural_notes": None,
            "word_count": 68,
            "estimated_duration_seconds": 34
        },
        {
            "chapter_id": "ch_03",
            "chapter_number": 3,
            "title": "तिसरा भाग: नाहक हस्तक्षेपाचे फळ आणि बोध",
            "content": (
                "माकडाने आपली सर्व शक्ती पणाला लावून ती लाकडी पाचर एका मोठ्या हिसक्यात बाहेर उपटून काढली!\n\n"
                "पाचर निघताच साठवून राहिलेला ताण प्रचंड गडगडाटासह मोकळा झाला, आणि त्या ओंडक्याचे दोन्ही महाकाय भाग विजेच्या वेगाने एकत्र मिटले. "
                "ते अडाणी माकड त्या लाकडी भेगेत क्षणात अडकून पडले.\n\n"
                "जेव्हा सुतार परत आले, तेव्हा त्यांनी पाहिले की नको त्या गोष्टीत नाक खुपसल्यामुळे माकडावर हा अनर्थ ओढवला होता.\n\n"
                "तात्पर्य: ज्या कामाचा आपल्याला अभ्यास नाही आणि ज्याच्याशी आपला संबंध नाही, त्यात कधीही पडू नये."
            ),
            "cultural_notes": "पंचतंत्रातील प्रसिद्ध मराठी नीतीबोध.",
            "word_count": 82,
            "estimated_duration_seconds": 41
        }
    ]
}

async def update_marathi_assets():
    tts = EdgeTTSProvider()
    base_dirs = [
        Path("storage/artifacts/story_panchatantra_monkey_wedge"),
        Path("backend/storage/artifacts/story_panchatantra_monkey_wedge")
    ]

    for base in base_dirs:
        for preset in ["quick", "standard"]:
            loc_dir = base / "localization" / "mr" / preset
            loc_dir.mkdir(parents=True, exist_ok=True)
            (loc_dir / "script.json").write_text(json.dumps(MARATHI_SCRIPT, indent=2, ensure_ascii=False), encoding="utf-8")

            aud_dir = base / "audio" / "mr" / preset
            aud_dir.mkdir(parents=True, exist_ok=True)
            chapters_meta = []
            total_sec = 0.0

            for idx, ch in enumerate(MARATHI_SCRIPT["chapters"], 1):
                fn = f"ch{idx:02d}.mp3"
                out_path = aud_dir / fn
                text = f"{ch['title']}.\n\n{ch['content']}"
                print(f"Synthesizing Marathi [{preset}] {fn} with AarohiNeural...")
                dur = await tts.synthesize(text, out_path, language="mr", voice="mr-IN-AarohiNeural")
                total_sec += dur
                chapters_meta.append({
                    "chapter_id": ch["chapter_id"],
                    "chapter_number": idx,
                    "title": ch["title"],
                    "audio_file": fn,
                    "duration_seconds": dur,
                    "file_size_bytes": out_path.stat().st_size
                })

            meta = {
                "story_id": "story_panchatantra_monkey_wedge",
                "language_code": "mr",
                "duration_preset": preset,
                "voice_id": "mr-IN-AarohiNeural",
                "total_duration_seconds": total_sec,
                "chapters": chapters_meta
            }
            (aud_dir / "asset_metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n✓ AUTHENTIC MARATHI SCRIPT & NEURAL AUDIO SYNTHESIZED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(update_marathi_assets())
