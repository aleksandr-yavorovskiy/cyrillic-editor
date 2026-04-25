<template>
  <div class="editor-page">
    <div class="toolbar">
      <button @click="showMarginsModal = true">
        Настроить отступы
      </button>

      <button @click="testBackend">Проверить соединение с сервером</button>
    
      <!-- TODO: Экспортировать в PDF -->
      <!-- TODO: ДОбавить хэлпер инструкцию (ctrl s - предвар просмотрет и тд) -->

      <!-- TODO: добавить возможность добавления шрифта вместе с маппингами символов 
       маппинги делать не jsonами а прям квадратиками напротив букв, и после этого уже будет конверт в json 
       1. валидировать шрифт
       2. -->

      <label>Шрифт:</label>
      <select v-model="selectedFont">
        <option v-for="font in fonts" :key="font" :value="font">
          {{ font }}
        </option>
      </select>

      <div class="font-size-control">
        <label>Размер шрифта:</label>
        <select v-model.number="fontSize">
          <option v-for="size in fontSizes" :key="size" :value="size">
            {{ size }}
          </option>
        </select>
      </div>

      <div class="toolbar-right">
        <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" />
        <button @click="$refs.fileInput.click()">Импортировать</button>
        <button @click="compileText">Компилировать PDF</button>
        <button @click="exportDocx">Экспорт в .docx</button>
      </div>
    </div>

    <div class="content">
      <textarea
        ref="textEditor"
        v-model="text"
        class="text-editor"
        :style="{ 
          fontFamily: selectedFont,
          fontSize: fontSize + 'pt'
        }"
      />

      <div class="pdf-preview">
        <iframe v-if="pdfUrl" :src="pdfUrl" frameborder="0"></iframe>
        <p v-else>PDF не скомпилирован</p>
      </div>
    </div>

    <div class="keyboard">
      <div class="keyboard-tabs">
        <label class="checkbox">
          <input type="checkbox" v-model="showUppercase" />
          Заглавные буквы
        </label>
        <button
          v-for="group in keyboard"
          :key="group.key"
          @click="activeTab = group.key"
          :class="{ active: activeTab === group.key }"
        >
          {{ group.label }}
        </button>
      </div>

      <div class="keyboard-content">

        <!-- TODO: use keyboard dictionary instead -->
        <button
          v-for="symbol in filterSymbols(
            keyboard.find(g => g.key === activeTab).symbols,
            activeTab
            )"
          :key="symbol"
          @click="insertSymbol(symbol)"
          :style="{ fontFamily: selectedFont }"
        >
          {{ symbol }}
        </button>
      </div>
    </div>
  </div>

  <div 
    v-if="showMarginsModal"
    class="modal-overlay"
    @click.self="showMarginsModal = false"
  >
    <div class="modal">
      <h3>Отступы (см)</h3>

      <div class="margins">
        <div v-for="(value, key) in margins" :key="key" class="margin-control">
          <label>
            {{
              {
                top: 'Сверху',
                bottom: 'Снизу',
                left: 'Слева',
                right: 'Справа'
              }[key]
            }}
          </label>

          <input
            type="number"
            step="0.5"
            min="0"
            v-model.number="margins[key]"
          />
        </div>
      </div>

      <div class="modal-actions">
        <button @click="showMarginsModal = false">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script>
import ponomar from '@/dictionaries/PonomarUnicode.json'
import bukyvede from '@/dictionaries/BukyVede.json'
import flavius from '@/dictionaries/FlaviusUniversal.json'
import menaion from '@/dictionaries/MenaionUnicode.json'
// TODO: add other fonts

import cyrillicLetters from '@/keyboard/cyrillic.json'
import slavicLetters from '@/keyboard/slavic.json'
import uppercaseSymbols from '@/keyboard/uppercase.json'
import diacriticSymbols from '@/keyboard/diacritic.json'
import punctuationSymbols from '@/keyboard/punctuation.json'


const API_URL = import.meta.env.VITE_API_URL

// TODO: компилировать автоматически по ctrl s

const dictionaries = {
  PonomarUnicode: ponomar,
  BukyVede: bukyvede,
  FlaviusUniversal: flavius,
  MenaionUnicode: menaion
// TODO: add other fonts
}

// TODO: ponomar: 2de1 п instead of в
function convertText(text, fromDict, toDict) {
  let result = ""

  for (let char of text) {
    let unicodeChar = char

    // old font -> unicode
    if (fromDict && char in fromDict.FontToUnicode) {
      unicodeChar = fromDict.FontToUnicode[char]
    }

    // unicode -> new font
    if (toDict && unicodeChar in toDict.UnicodeToFont) {
      result += toDict.UnicodeToFont[unicodeChar]
    } else {
      result += unicodeChar
    }
  }

  return result
}

export default {
  data() {
    return {
      text: '',
      pdfUrl: '',
      keyboard: [
        {
          key: 'cyrillic', // TODO: change to churchslavonic?
          label: 'Церковнославянский',
          symbols: cyrillicLetters
        },
        {
          key: 'slavic',
          label: 'Доп. старославянский',
          symbols: slavicLetters
        },
        {
          key: 'uppercase',
          label: 'Буквотитла',
          symbols: uppercaseSymbols
        },
        {
          key: 'superscript',
          label: 'Диакритика',
          symbols: diacriticSymbols
        },
        {
          key: 'punctuation',
          label: 'Пунктуация',
          symbols: punctuationSymbols
        },
      ],
      activeTab: 'cyrillic',
      showUppercase: true,
      fonts: [
        'PonomarUnicode',
        'FlaviusUniversal',
        'FlavExpUniversal',
        'MenaionUnicode', // TODO: menaion
        'Bukyvede' // TODO: BukyVede?
      ],
      selectedFont: 'PonomarUnicode',
      fontSizes: [
        8, 9, 10, 11, 12, 14, 16, 18,
        20, 22, 24, 26, 28, 32, 36,
        40, 48, 56, 64, 72
      ],
      fontSize: 14,
      showMarginsModal: false,
      margins: {
        top: 2,
        bottom: 2,
        left: 2,
        right: 2
      },
    };
  },
  watch: {
    selectedFont(newFont, oldFont) {
      const fromDict = dictionaries[oldFont]
      const toDict = dictionaries[newFont]

      this.text = convertText(this.text, fromDict, toDict)
    }
  },
  methods: {
    filterSymbols(symbols, tabKey) {
      if (tabKey !== 'cyrillic') return symbols // TODO: add slavic also

      if (this.showUppercase) return symbols

      return symbols.filter(s => s !== s.toUpperCase())
    },
    exportDocx() {
      fetch(`${API_URL}/api/export-docx/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: this.text,
          fontSize: this.fontSize, // TODO: margins? font?
        }),
      })
        .then(response => response.blob())
        .then(blob => {
          const url = window.URL.createObjectURL(blob)

          const a = document.createElement('a')
          a.href = url
          a.download = 'document.docx'
          a.click()

          window.URL.revokeObjectURL(url)
        })
        .catch(err => {
          console.error(err)
          alert('Ошибка экспорта.')
        })
    },
    testBackend() {
      fetch(`${API_URL}/api/ping/`)
        .then(res => res.json())
        .then(data => {
          alert(data.message);
        })
        .catch(err => {
          console.error(err);
          alert(`Error connecting to backend. API_URL:${API_URL}`);
        });
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("file", file);

      fetch(`${API_URL}/api/import/`, {
        method: 'POST',
        body: formData,
      })
        .then(res => res.json())
        .then(data => {
          console.log(data);
          if (data.text) {
            this.text = data.text;
          } else {
            alert("Файл обработан, но текст не получен");
          }
        })
        .catch(err => {
          console.error(err);
          alert("Ошибка загрузки файла");
        });
    },
    compileText() {
      fetch(`${API_URL}/api/compile/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: this.text,
          font: this.selectedFont,
          fontSize: this.fontSize,
          top: this.margins.top,
          bottom: this.margins.bottom,
          left: this.margins.left,
          right: this.margins.right,
        }),
      })
        .then((response) => response.blob())
        .then((blob) => {
          this.pdfUrl = URL.createObjectURL(blob);
        })
        .catch((error) => {
          alert('Error compiling text:', error);
        });
    },
    insertSymbol(symbol) {
      const textarea = this.$refs.textEditor;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;

      this.text =
        this.text.slice(0, start) +
        symbol +
        this.text.slice(end);

      this.$nextTick(() => {
        textarea.focus();
        textarea.selectionStart = textarea.selectionEnd = start + symbol.length;
      });
    }
  },
};
</script>

<style scoped>
.editor-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f7f8fa;
  font-family: system-ui, -apple-system, sans-serif;
}

.toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 15px;
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
}

.toolbar button,
.toolbar select {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar button:hover {
  background: #f0f0f0;
}

.toolbar button:active {
  transform: scale(0.97);
}

.toolbar-right {
  margin-left: auto;
  display: flex;
  gap: 10px;
  align-items: center;
}

.content {
  display: flex;
  flex: 1;
  gap: 10px;
  padding: 10px;
}

.text-editor {
  flex: 1;
  padding: 15px;
  font-size: 18px;
  border-radius: 10px;
  border: 1px solid #ddd;
  outline: none;
  resize: none;
  background: white;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.text-editor:focus {
  border-color: #4a90e2;
}

.pdf-preview {
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  background: white;
  border: 1px solid #ddd;
  display: flex;
  flex-direction: column;
}

.pdf-preview iframe {
  flex: 1;
  width: 100%;
  border: none;
}

.keyboard {
  display: flex;
  flex-direction: column;
  height: 280px;
  background: #ffffff;
  border-top: 1px solid #ddd;
}

.keyboard-tabs {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px;
  border-bottom: 1px solid #eee;
}

.keyboard-tabs button {
  padding: 6px 10px;
  border: none;
  background: #f2f2f2;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}

.keyboard-tabs button:hover {
  background: #e0e0e0;
}

.keyboard-tabs button.active {
  background: #4a90e2;
  color: white;
}

.checkbox {
  margin-right: 10px;
  font-size: 14px;
}

.keyboard-content {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
  gap: 6px;
  padding: 8px;
}

.keyboard-content button {
  padding: 10px;
  font-size: 22px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.15s;
}

.keyboard-content button:hover {
  background: #eaeaea;
}

.keyboard-content button:active {
  transform: scale(0.92);
  background: #dcdcdc;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.35);

  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: white;
  padding: 20px;
  border-radius: 12px;
  min-width: 320px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.modal h3 {
  margin-bottom: 15px;
}

.margins {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.margin-control {
  display: flex;
  flex-direction: column;
  font-size: 14px;
}

.margin-control input {
  margin-top: 4px;
  padding: 6px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.modal-actions {
  margin-top: 15px;
  text-align: right;
}

.modal-actions button {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  background: #4a90e2;
  color: white;
  cursor: pointer;
}

.font-size-control {
  display: flex;
  align-items: center;
  gap: 6px;
}

.font-size-control select {
  padding: 4px 6px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

@font-face {
  font-family: 'BukyVede';
  src: url('/fonts/BukyVede.ttf'); /* TODO: BukyVede */
}

@font-face {
  font-family: 'FlaviusUniversal';
  src: url('/fonts/FlaviusUniversal.ttf');
}

@font-face {
  font-family: 'FlavExpUniversal';
  src: url('/fonts/FlavExpUniversal.ttf');
}

@font-face {
  font-family: 'MenaionUnicode';
  src: url('/fonts/MenaionUnicode.otf'); /* TODO: MenaionUnicode */
}

@font-face {
  font-family: 'PonomarUnicode';
  src: url('/fonts/PonomarUnicode.otf');
}

</style>