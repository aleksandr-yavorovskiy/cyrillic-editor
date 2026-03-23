<template>
  <div class="editor-page">
    <div class="toolbar">
      <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" />
      <button @click="$refs.fileInput.click()">Импортировать</button>

      <button @click="compileText">Compile</button>
      <button @click="testBackend">Test Backend</button>
      <select v-model="selectedFont">
        <option value="default">Default Font</option>
        <!-- TODO: get available fonts, use here -->
      </select>
    </div>

    <div class="content">
      <textarea v-model="text" class="text-editor"></textarea>
      <div class="pdf-preview">
        <iframe v-if="pdfUrl" :src="pdfUrl" frameborder="0"></iframe>
        <p v-else>No preview available</p>
      </div>
    </div>

    <div class="keyboard">
      <button v-for="symbol in cyrillicSymbols" :key="symbol" @click="insertSymbol(symbol)">
        {{ symbol }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      text: '',
      selectedFont: 'default',
      pdfUrl: '',
      cyrillicSymbols: ['Ѧ', 'Ѫ', '҂', '҃', '҄'], // TODO: change symbols, get from dictionary
    };
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
      this.text += symbol;
    },
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
}

.keyboard {
  display: flex;
  flex-wrap: wrap;
  padding: 10px;
  background-color: #f9f9f9;
}

.keyboard button {
  margin: 5px;
  padding: 10px;
  font-size: 16px;
}
</style>