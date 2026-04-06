<template>
  <div class="editor-page">
    <div class="toolbar">
      <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" />
      <button @click="$refs.fileInput.click()">Импортировать</button>

      <button @click="showMarginsModal = true">
        Настроить отступы
      </button>

      <button @click="compileText">Компилировать</button>
      <button @click="exportDocx">Экспорт в .docx</button>
      <!-- <button @click="testBackend">Проверить соединение с сервером</button> -->
      <select v-model="selectedFont">
        <option v-for="font in fonts" :key="font" :value="font">
          {{ font }}
        </option>
      </select>
    </div>

    <div class="content">
      <textarea
        ref="textEditor"
        v-model="text"
        class="text-editor"
        :style="{ fontFamily: selectedFont }"
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

const dictionaries = {
  PonomarUnicode: ponomar,
  BukyVede: bukyvede,
  FlaviusUniversal: flavius,
  MenaionUnicode: menaion
// TODO: add other fonts
}

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
          key: 'cyrillic',
          label: 'Кириллица',
          symbols: cyrillicLetters
        },
        {
          key: 'slavic',
          label: 'Доп. старославянские',
          symbols: slavicLetters
        },
        {
          key: 'uppercase',
          label: 'Выносные',
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
        'menaionunicode', // TODO: menaion
        'bukyvede' // TODO: BukyVede?
      ],
      selectedFont: 'PonomarUnicode',
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
      if (tabKey !== 'cyrillic') return symbols

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
}

.toolbar {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f0f0f0;
}

.margins {
  display: flex;
  gap: 10px;
}

.margin-control {
  display: flex;
  align-items: center;
  gap: 5px;
}

.margin-control input {
  width: 50px;
  text-align: center;
}

.margin-control button {
  width: 30px;
  height: 30px;
  cursor: pointer;
}

.content {
  display: flex;
  flex: 1;
}

.text-editor {
  flex: 1;
  padding: 10px;
  font-size: 16px;
}

.pdf-preview {
  flex: 1;
  padding: 10px;
  border-left: 1px solid #ccc;
  display: flex;
  flex-direction: column;
}

.pdf-preview iframe {
  flex: 1;
  width: 100%;
  height: 100%;
  border: none;
}

.keyboard {
  display: flex;
  flex-direction: column;
  height: 300px;
  border-top: 1px solid #ccc;
}

.keyboard-tabs {
  display: flex;
}

.keyboard-content {
  flex: 1;
  overflow-y: auto;
  /* display: grid; */
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 5px;
  padding: 5px;
}

.keyboard button {
  margin: 5px;
  padding: 10px;
  font-size: 30px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);

  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: white;
  padding: 20px;
  border-radius: 10px;
  min-width: 300px;
}

.modal-actions {
  margin-top: 15px;
  text-align: right;
}

@font-face {
  font-family: 'BukyVede';
  src: url('/fonts/bukyvede.ttf'); /* TODO: BukyVede */
}

@font-face {
  font-family: 'FlaviusUniversal';
  src: url('/fonts/FlaviusUniversal.ttf');
}

/* TODO: add flavexp */
@font-face {
  font-family: 'FlavExpUniversal';
  src: url('/fonts/FlavExpUniversal.ttf');
}

@font-face {
  font-family: 'MenaionUnicode';
  src: url('/fonts/menaionunicode.otf'); /* TODO: MenaionUnicode */
}

@font-face {
  font-family: 'PonomarUnicode';
  src: url('/fonts/PonomarUnicode.otf');
}

</style>