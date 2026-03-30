<template>
  <div class="editor-page">
    <div class="toolbar">
      <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" />
      <button @click="$refs.fileInput.click()">Импортировать</button>

      <button @click="compileText">Компилировать</button>
      <button @click="testBackend">Проверить соединение с сервером</button>
      <select v-model="selectedFont">
        <option v-for="font in fonts" :key="font" :value="font">
          {{ font }}
        </option>
      </select>
    </div>

    <div class="content">
      <textarea
        v-model="text"
        class="text-editor"
        :style="{ fontFamily: selectedFont }"
      />

      <div class="pdf-preview">
        <iframe v-if="pdfUrl" :src="pdfUrl" frameborder="0"></iframe>
        <p v-else>No preview available</p>
      </div>
    </div>

    <div class="keyboard">
      <div class="keyboard-tabs">
        <button
          v-for="group in keyboard"
          :key="group.key"
          @click="activeTab = group.key"
        >
          {{ group.label }}
        </button>
      </div>

      <div class="keyboard-content">
        <button
          v-for="symbol in keyboard.find(g => g.key === activeTab).symbols"
          :key="symbol"
          @click="insertSymbol(symbol)"
        >
          {{ symbol }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import ponomar from '@/dictionaries/PonomarUnicode.json'
import bukyvede from '@/dictionaries/bukyvede.json'
import flavius from '@/dictionaries/FlaviusUniversal.json'

const dictionaries = {
  PonomarUnicode: ponomar,
  BukyVede: bukyvede,
  FlaviusUniversal: flavius,
}

function convertText(text, fromDict, toDict) {
  let result = ""

  for (let char of text) {
    let unicodeChar = char

    // old font -> unicode
    if (fromDict && fromDict.FontToUnicode[char]) {
      unicodeChar = fromDict.FontToUnicode[char]
    }

    // unicode -> new font
    if (toDict && toDict.UnicodeToFont[unicodeChar]) {
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
          symbols: ['Ѣ','ѣ','Ѳ','ѳ','Ѵ','ѵ','Ѧ','ѧ','Ѫ','ѫ']
        },
        {
          key: 'uppercase',
          label: 'выносные',
          symbols: [' ⷠ','ⷡ',' ⷢ']
        },
        {
          key: 'superscript',
          label: 'Диакритика',
          symbols: ['҃','҄','҅','҆','҇']
        },
        // {
        //   key: 'titlo',
        //   label: 'Титла',
        //   symbols: ['҃','҇']
        // }
      ], // TODO: change symbols, get from dictionary
      activeTab: 'cyrillic',
      fonts: [
        'PonomarUnicode',
        'FlaviusUniversal',
        'FlavExpUniversal',
        'menaionunicode',
        'bukyvede' // TODO: BukyVede?
      ],
      selectedFont: 'PonomarUnicode',
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
    testBackend() {
      fetch('/api/ping/')
        .then(res => res.json())
        .then(data => {
          alert(data.message);
        })
        .catch(err => {
          console.error(err);
          alert("Error connecting to backend");
        });
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("file", file);

      fetch('/api/import/', {
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
      fetch('/api/compile/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: this.text,
          font: this.selectedFont,
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
      const textarea = this.$el.querySelector('.text-editor');
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
  height: 150px;
  border-top: 1px solid #ccc;
}

.keyboard-tabs {
  display: flex;
}

.keyboard-content {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 5px;
  padding: 5px;
}

.keyboard button {
  margin: 5px;
  padding: 10px;
  font-size: 16px;
}

@font-face {
  font-family: 'BukyVede';
  src: url('/fonts/bukyvede.ttf');
}

@font-face {
  font-family: 'FlaviusUniversal';
  src: url('/fonts/FlaviusUniversal.ttf');
}

/* TODO: add flavexp */

@font-face {
  font-family: 'MenaionUnicode';
  src: url('/fonts/menaionunicode.otf');
}

@font-face {
  font-family: 'PonomarUnicode';
  src: url('/fonts/PonomarUnicode.otf');
}

</style>