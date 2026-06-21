import asyncio
import edge_tts
import os
import time
import sys

# Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def header():
    os.system('clear')
    print(f"{MAGENTA}{BOLD}╔════════════════════════════════════════════════╗")
    print(f"║         SSC 26 AI VOICE ENGINE (GIRL)          ║")
    print(f"╚════════════════════════════════════════════════╝{RESET}")
    print(f"{RED} [e] Exit | [b] Back (Prev Step){RESET}")

def count_letters(text):
    """Count actual letters/characters excluding whitespace"""
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))

async def main():
    step = 1
    data = {
        "voice": "",
        "text": "",
        "speed": "",
        "filename": ""
    }

    while True:
        header()
        
        # --- STEP 1: VOICE SELECTION ---
        if step == 1:
            print(f"\n{YELLOW}{BOLD}➤ STEP 1: Select Female Voice{RESET}")
            print(f"{CYAN}   [1] Nabanita (BD)    | [2] Tanishaa (IN)")
            print(f"   [3] Pradeep (BD-M)   | [4] Bashkar (IN-M){RESET}")
            print(f"{YELLOW}   NOTE: Only Nabanita & Tanishaa are confirmed Female voices{RESET}")
            u_input = input(f"\n{BOLD}   Choice (1-4): {RESET}").strip().lower()
            
            if u_input == 'e': sys.exit()
            if u_input in ["1", "2", "3", "4"]:
                # FIXED: Correct voice names from Microsoft official list
                voices = {
                    "1": "bn-BD-NabanitaNeural",    # Female - Bangladesh
                    "2": "bn-IN-TanishaaNeural",    # Female - India (FIXED: was TanishaNeural)
                    "3": "bn-BD-PradeepNeural",     # Male - Bangladesh
                    "4": "bn-IN-BashkarNeural"      # Male - India
                }
                data["voice"] = voices[u_input]
                step = 2
            else: continue

        # --- STEP 2: INPUT METHOD ---
        elif step == 2:
            print(f"\n{YELLOW}{BOLD}➤ STEP 2: Input Method{RESET}")
            print(f"   [1] input.txt file | [2] Direct Paste")
            u_input = input(f"\n{BOLD}   Choice (1-2): {RESET}").strip().lower()

            if u_input == 'e': sys.exit()
            if u_input == 'b': step = 1; continue
            
            if u_input == "2":
                data["text"] = input(f"\n{BOLD}   Bangla text paste korun: {RESET}").strip()
                if data["text"]: step = 3
            elif u_input == "1":
                if not os.path.exists("input.txt"):
                    print(f"{RED}   [!] Error: input.txt file pawa jayni!{RESET}")
                    time.sleep(1.5); continue
                with open("input.txt", "r", encoding="utf-8") as f:
                    data["text"] = f.read().strip()
                letter_count = count_letters(data["text"])
                print(f"{GREEN}   ✔ File loaded! Total letters: {letter_count}{RESET}")
                time.sleep(1)
                step = 3
            else: continue

        # --- STEP 3: SPEED CONTROL ---
        elif step == 3:
            print(f"\n{YELLOW}{BOLD}➤ STEP 3: Speed Control{RESET}")
            u_input = input(f"{BOLD}   Speed (Ex: 1.3): {RESET}").strip().lower()

            if u_input == 'e': sys.exit()
            if u_input == 'b': step = 2; continue
            
            try:
                speed_val = float(u_input)
                change = int((speed_val - 1) * 100)
                data["speed"] = f"{'+' if change >= 0 else ''}{change}%"
                step = 4
            except:
                print(f"{RED}   [!] Valid number din (Ex: 1.5){RESET}")
                time.sleep(1)

        # --- STEP 4: FILENAME & GENERATE ---
        elif step == 4:
            print(f"\n{YELLOW}{BOLD}➤ STEP 4: Save Configuration{RESET}")
            u_input = input(f"{BOLD}   Audio-r nam ki hobe? : {RESET}").strip().lower()

            if u_input == 'e': sys.exit()
            if u_input == 'b': step = 3; continue
            
            if not u_input: u_input = "output"
            data["filename"] = u_input if u_input.endswith(".mp3") else u_input + ".mp3"

            letter_count = count_letters(data["text"])
            print(f"\n{CYAN}   📄 Text length: {letter_count} letters{RESET}")
            print(f"{GREEN}{BOLD}   [●] Generating... Please wait.{RESET}")
            
            try:
                communicate = edge_tts.Communicate(data["text"], data["voice"], rate=data["speed"])
                
                # Progress tracking
                total_chars = len(data["text"])
                processed = 0
                
                # Use stream to track progress
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                        # Simple progress estimation based on text length
                        processed = min(processed + len(chunk["data"]), total_chars * 100)
                        percent = min(int((len(audio_data) / (total_chars * 50)) * 100), 99)
                        print(f"\r{CYAN}   ⏳ Progress: {percent}% {RESET}", end="", flush=True)
                
                # Save the file
                with open(data["filename"], "wb") as f:
                    f.write(audio_data)
                
                print(f"\r{GREEN}   ✔ Progress: 100% {RESET}")
                print(f"\n{BLUE}════════════════════════════════════════════════")
                print(f"{GREEN}{BOLD}   ✔ GENERATION COMPLETE!")
                print(f"   📁 Saved as: {data['filename']}")
                print(f"   📊 Total letters: {letter_count}")
                print(f"   🎙️  Voice: {data['voice']}")
                print(f"   ⚡ Speed: {data['speed']}{RESET}")
                print(f"{BLUE}════════════════════════════════════════════════{RESET}")
                input(f"\n{CYAN}Main menu-te firte Enter chapun...{RESET}")
                step = 1
            except Exception as e:
                print(f"\n{RED}   [!] Error: {e}{RESET}")
                print(f"{YELLOW}   💡 Try: pip install --upgrade edge-tts{RESET}")
                time.sleep(3); step = 1

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()
