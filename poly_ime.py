import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from keycodes import *  # for VK_XXX constants
from textService import *
from multilingual_ime.key_event_handler import KeyEventHandler

print("PolyKey IME Loaded")
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# 選單項目和語言列按鈕的 command ID
ID_SWITCH_LANG = 1
ID_SWITCH_SHAPE = 2
ID_SETTINGS = 3
ID_MODE_ICON = 4
ID_ABOUT = 5
ID_WEBSITE = 6
ID_GROUP = 7
ID_BUGREPORT = 8
ID_DICT_BUGREPORT = 9
ID_CHEWING_HELP = 10
ID_HASHED = 11
ID_MOEDICT = 13
ID_DICT = 14
ID_SIMPDICT = 15
ID_LITTLEDICT = 16
ID_PROVERBDICT = 17
ID_OUTPUT_SIMP_CHINESE = 18
ID_USER_PHRASE_EDITOR = 19

# 設定輸入法
ID_BOPOMOFO_IME = 20
ID_CANGJIE_IME = 21
ID_ENGLISH_IME = 22
ID_PINYIN_IME = 23
ID_JAPANESE_IME = 24
ID_SPECIAL_IME = 25

# 按鍵內碼和名稱的對應
keyNames = {
    VK_ESCAPE: "Esc",
    VK_RETURN: "Enter",
    VK_TAB: "Tab",
    VK_DELETE: "Del",
    VK_BACK: "Backspace",
    VK_UP: "Up",
    VK_DOWN: "Down",
    VK_LEFT: "Left",
    VK_RIGHT: "Right",
    VK_HOME: "Home",
    VK_END: "End",
    VK_PRIOR: "PageUp",
    VK_NEXT: "PageDown",
}

# PolyKey Logger
local_appdata = os.getenv("LOCALAPPDATA")
if local_appdata is None:
    raise EnvironmentError("LOCALAPPDATA environment variable is not set.")

log_file_path = Path(local_appdata) / "PIME" / "polykey" / "polykey.log"

if not log_file_path.exists():
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    log_file_path.write_text("")

LOG_MODE = logging.DEBUG

logger = logging.getLogger(f"{__name__}")
logger.setLevel(LOG_MODE)

file_handler = RotatingFileHandler(
    log_file_path, encoding="utf-8", maxBytes=1024 * 1024, backupCount=1
)
file_handler.setLevel(LOG_MODE)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.info("PolyKey Logger Initialized")


# Host Test Path
host_test_path = Path(__file__).parent / "T" / "host_test.py"

script_path = Path(__file__)


class PolyTextService(TextService):
    def __init__(self, client):
        TextService.__init__(self, client)
        self.curdir = os.path.abspath(os.path.dirname(__file__))
        self.icon_dir = os.path.join(self.curdir, "icons")
        self.my_key_event_handler = KeyEventHandler(verbose_mode=True)

        # States
        self.in_typing_mode = False
        self.langMode = None

        # Variables
        self.composition_string = ""
        self._run_timer = None

        self.last_composition_string = ""

        self.customizeUI(
            candFontName="MingLiu", candFontSize=16, candPerRow=1, candUseCursor=True
        )

        self.last_seqNum = None

    def onActivate(self):
        TextService.onActivate(self)
        logger.info("PolyKey Activated")
        self.addLangButtons()

    def removeLangButtons(self):
        # TODO
        pass

    def onDeactivate(self):
        logger.info("PolyKey Deactivated")
        self.in_typing_mode = False
        pass

    def setAutoLearn(self, autoLearn):
        # TODO
        pass

    def onCompositionTerminated(self, forced):
        self.my_key_event_handler.handle_key("enter")

    def convertKeyEvent(self, key_event):
        char_code = key_event.charCode
        key_code = key_event.keyCode
        char_str = chr(char_code)

        key_event = ""
        if key_code == VK_RETURN:
            key_event = "enter"
        elif key_code == VK_LEFT:
            key_event = "left"
        elif key_code == VK_RIGHT:
            key_event = "right"
        elif key_code == VK_UP:
            key_event = "up"
        elif key_code == VK_DOWN:
            key_event = "down"
        elif key_code == VK_BACK:
            key_event = "backspace"
        elif key_code == VK_DELETE:
            key_event = "delete"
        elif key_code == VK_ESCAPE:
            key_event = "esc"
        elif key_code == VK_SPACE:
            key_event = "space"
        elif key_code == VK_SHIFT:
            key_event = "shift"
        elif key_code == VK_CONTROL:
            key_event = "ctrl"
        else:
            key_event = char_str

        return key_event

    def updateUI(self):
        logger.info("Updating UI")
        if self.my_key_event_handler.in_selection_mode:
            self.setShowCandidates(True)
            self.setCandidateList(self.my_key_event_handler.candidate_word_list)
            self.setCandidateCursor(self.my_key_event_handler.selection_index)
        else:
            if (commit_string := self.my_key_event_handler.commit_string) != "":
                self.setCommitString(commit_string)
                self.in_typing_mode = False

            self.setShowCandidates(False)
            self.setCompositionString(self.my_key_event_handler.composition_string)
            composition_token_index = self.my_key_event_handler.composition_index
            composition_index = len(
                "".join(
                    self.my_key_event_handler.total_composition_words[
                        :composition_token_index
                    ]
                )
            )

            self.setCompositionCursor(composition_index)
            self.last_composition_string = self.my_key_event_handler.composition_string

    def slow_updateUI(self):
        self.my_key_event_handler.slow_handle()
        self.updateUI()

    def onKeyDown(self, keyEvent):
        key_event = self.convertKeyEvent(keyEvent)

        functional_keys = [
            "up",
            "down",
            "left",
            "right",
            "tab",
            "enter",
            "backspace",
            "escape",
        ]

        if self.in_typing_mode:
            # Handle normally
            pass
        else:
            if key_event in functional_keys:
                return False
            else:
                # Open typing mode and handle key
                self.in_typing_mode = True

        logger.info("key_event: %s", key_event)
        self.my_key_event_handler.handle_key(key_event)
        self.my_key_event_handler.slow_handle()
        self.updateUI()
        return True

    def filterKeyUp(self, keyEvent):
        return True

    def onKeyUp(self, keyEvent):
        return True

    def filterKeyDown(self, keyEvent):
        return True


    def onMenu(self, buttonId):
        if buttonId == "settings" or buttonId == "windows-mode-icon":
            # 用 json 語法表示選單結構
            return [
                # {"text": "多語言輸入法使用說明 (&H)", "id": ID_CHEWING_HELP},
                # {"text": "編輯使用者詞庫 (&E)", "id": ID_USER_PHRASE_EDITOR},
                # {"text": "設定多語言輸入法(&W)", "id": ID_SETTINGS},
                # {},
                {
                    "text": (
                        "✔"
                        if "bopomofo" in self.my_key_event_handler.activated_imes
                        else "✘"
                    )
                    + " | 注音輸入法(&1)",
                    "id": ID_BOPOMOFO_IME,
                },
                {
                    "text": (
                        "✔"
                        if "english" in self.my_key_event_handler.activated_imes
                        else "✘"
                    )
                    + " | 英文輸入法(&2)",
                    "id": ID_ENGLISH_IME,
                },
                {
                    "text": (
                        "✔"
                        if "cangjie" in self.my_key_event_handler.activated_imes
                        else "✘"
                    )
                    + " | 倉頡輸入法(&3)",
                    "id": ID_CANGJIE_IME,
                },
                {
                    "text": (
                        "✔"
                        if "pinyin" in self.my_key_event_handler.activated_imes
                        else "✘"
                    )
                    + " | 拼音輸入法(&4)",
                    "id": ID_PINYIN_IME,
                },
                {
                    "text": (
                        "✔"
                        if "japanese" in self.my_key_event_handler.activated_imes
                        else "✘"
                    )
                    + " | 日文輸入法(&5)",
                    "id": ID_JAPANESE_IME,
                },
                {},
                {"text": "回報問題(&B)", "id": ID_BUGREPORT},
                {"text": "GitHub Repo(&W)", "id": ID_WEBSITE},
            ]
        else:
            logger.warning("Unknown buttonId: %s", buttonId)
            return []

    def onCommand(self, commandId, commandType):
        if commandId == ID_SETTINGS:
            pass
        elif commandId == ID_BOPOMOFO_IME:
            self.my_key_event_handler.set_activation_status(
                "bopomofo", not "bopomofo" in self.my_key_event_handler.activated_imes
            )
        elif commandId == ID_CANGJIE_IME:
            self.my_key_event_handler.set_activation_status(
                "cangjie", not "cangjie" in self.my_key_event_handler.activated_imes
            )
        elif commandId == ID_ENGLISH_IME:
            self.my_key_event_handler.set_activation_status(
                "english", not "english" in self.my_key_event_handler.activated_imes
            )
        elif commandId == ID_PINYIN_IME:
            self.my_key_event_handler.set_activation_status(
                "pinyin", not "pinyin" in self.my_key_event_handler.activated_imes
            )
        elif commandId == ID_JAPANESE_IME:
            self.my_key_event_handler.set_activation_status(
                "japanese", not "japanese" in self.my_key_event_handler.activated_imes
            )
        elif commandId == ID_BUGREPORT:
            os.startfile("https://github.com/Zen-Transform/polykey-win/issues")
        elif commandId == ID_WEBSITE:
            os.startfile("https://github.com/Zen-Transform/polykey-win")
        else:
            logger.warning("Unknown commandId: %s", commandId)

    def addLangButtons(self):
        self.addButton(
            "windows-mode-icon",
            icon=(Path(__file__).parent / "icons" / "config.ico").as_posix(),
            tooltip="中英文切換",
            commandId=ID_MODE_ICON,
        )