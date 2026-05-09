<template>
  <div class="editor-page">
    <div class="toolbar">
      <button @click="showHelpModal = true" title="Справка (F1)">Справка</button>
      <button @click="showMarginsModal = true">Настроить отступы</button>

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
        <button @click="convertToGlagolitic">Конвертировать в глаголицу</button>
        <button @click="convertToCyrillic">Конвертировать в кириллицу</button>
        <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" />
        <button @click="triggerFileImport">Импортировать...</button>
        <button @click="compileText" :disabled="isCompiling">
          {{ isCompiling ? 'Компиляция...' : 'Предпросмотр PDF' }}
        </button>
        <button @click="exportPdf" :disabled="isExporting">
          {{ isExporting ? 'Экспорт...' : 'Экспорт в PDF' }}
        </button>
        <button @click="exportDocx" :disabled="isExporting">
          {{ isExporting ? 'Экспорт...' : 'Экспорт в .docx' }}
        </button>
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
        @keydown.ctrl.s.prevent="compileText"
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
        <button
          v-for="symbol in activeSymbols"
          :key="symbol"
          @click="insertSymbol(symbol)"
          :style="{ fontFamily: selectedFont }"
        >
          {{ symbol }}
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="error-toast" @click="errorMessage = ''">
      {{ errorMessage }}
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
          <label>{{ marginLabels[key] }}</label>
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

  <div
    v-if="showHelpModal"
    class="modal-overlay"
    @click.self="showHelpModal = false"
  >
    <div class="modal help-modal">
      <h3>Справка по использованию редактора</h3>

      <div class="help-section">
        <h4>Принцип работы:</h4>
        <ul>
          <li>Текст набирается в левой половине экрана, предпросмотр PDF осуществляется в правой половине.</li>
          <li>Для настройки, импорта и экспорта используется верхнее меню с кнопками.</li>
          <li>Для набора специальных символов используется экранная клавиатура, расположенная в нижней части экрана.</li>
        </ul>
      </div>

      <div class="help-section">
        <h4>Кнопки панели инструментов:</h4>
        <ul>
          <li><strong>Настроить отступы</strong> — открывает окно для настройки полей страницы (сверху, снизу, слева, справа) в сантиметрах.</li>
          <li><strong>Шрифт</strong> — выбор шрифта для отображения текста (PonomarUnicode, BukyVede и др.).</li>
          <li><strong>Размер шрифта</strong> — выбор размера шрифта от 8 до 72 pt.</li>
          <li><strong>Конвертировать в глаголицу</strong> — преобразует набранный кириллический текст в глаголицу.</li>
          <li><strong>Конвертировать в кириллицу</strong> — преобразует набранный текст на глаголице в кириллицу.</li>
          <li><strong>Импортировать</strong> — загрузка текста из файла (.txt, .pdf, .docx).</li>
          <li><strong>Предпросмотр PDF</strong> — компилирует текст и показывает PDF-предпросмотр справа.</li>
          <li><strong>Экспортировать в PDF</strong> — скачивает PDF-файл с набранным текстом.</li>
          <li><strong>Экспорт в .docx</strong> — скачивает набранный текст в формате Word.</li>
        </ul>
      </div>

      <div class="help-section">
        <h4>Экранная клавиатура:</h4>
        <ul>
          <li><strong>Заглавные буквы</strong> — галочка для отображения/скрытия заглавных букв в кириллице.</li>
          <li><strong>Кириллица</strong> — вкладка с буквами кириллицы (в т.ч. старославянский, церковнославянский).</li>
          <li><strong>Буквотитла</strong> — вкладка с надстрочными буквами (буквотитла).</li>
          <li><strong>Диакритика</strong> — вкладка с диакритическими знаками.</li>
          <li><strong>Пунктуация</strong> — вкладка со знаками препинания.</li>
          <li><strong>Глаголица</strong> — вкладка с глаголическими буквами.</li>
          <li>Нажмите на любой символ на клавиатуре, чтобы вставить его в текст в позиции курсора.</li>
        </ul>
      </div>

      <div class="help-section">
        <h4>Горячие клавиши:</h4>
        <ul>
          <li><strong>F1</strong> — открыть справку.</li>
          <li><strong>Esc</strong> — закрыть справку.</li>
          <li><strong>Ctrl+S</strong> — скомпилировать и показать предпросмотр PDF.</li>
        </ul>
      </div>

      <div class="modal-actions">
        <button @click="showHelpModal = false">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script>
import ponomar from '@/dictionaries/PonomarUnicode.json'
import bukyvede from '@/dictionaries/BukyVede.json'
import flavius from '@/dictionaries/FlaviusUniversal.json'
import flavexp from '@/dictionaries/FlavExpUniversal.json'
import menaion from '@/dictionaries/MenaionUnicode.json'

import cyrillicLetters from '@/keyboard/cyrillic.json'
import glagoliticLetters from '@/keyboard/glagolitic.json'
import glagolitic from '@/dictionaries/glagolitic.json'
import uppercaseSymbols from '@/keyboard/uppercase.json'
import diacriticSymbols from '@/keyboard/diacritic.json'
import punctuationSymbols from '@/keyboard/punctuation.json'

import { compileText, exportPdf, exportDocx, importFile, downloadPdfBlob, downloadDocxBlob } from '@/api/editor'
import { convertText, convertDirect } from '@/utils/conversions'

const dictionaries = {
  PonomarUnicode: ponomar,
  BukyVede: bukyvede,
  FlaviusUniversal: flavius,
  FlavExpUniversal: flavexp,
  MenaionUnicode: menaion
}

export default {
  data() {
    return {
      text: '',
      pdfUrl: '',
      keyboard: [
        { key: 'cyrillic', label: 'Кириллица', symbols: cyrillicLetters },
        { key: 'uppercase', label: 'Буквотитла', symbols: uppercaseSymbols },
        { key: 'superscript', label: 'Диакритика', symbols: diacriticSymbols },
        { key: 'punctuation', label: 'Пунктуация', symbols: punctuationSymbols },
        { key: 'glagolitic', label: 'Глаголица', symbols: glagoliticLetters },
      ],
      activeTab: 'cyrillic',
      showUppercase: true,
      fonts: [
        'PonomarUnicode',
        'FlaviusUniversal',
        'FlavExpUniversal',
        'MenaionUnicode',
        'Bukyvede'
      ],
      selectedFont: 'PonomarUnicode',
      fontSizes: [
        8, 9, 10, 11, 12, 14, 16, 18,
        20, 22, 24, 26, 28, 32, 36,
        40, 48, 56, 64, 72
      ],
      fontSize: 14,
      showMarginsModal: false,
      showHelpModal: false,
      errorMessage: '',
      isCompiling: false,
      isExporting: false,
      margins: {
        top: 2,
        bottom: 2,
        left: 2,
        right: 2
      },
    }
  },
  computed: {
    marginLabels() {
      return {
        top: 'Сверху',
        bottom: 'Снизу',
        left: 'Слева',
        right: 'Справа'
      }
    },
    activeKeyboardGroup() {
      return this.keyboard.find(g => g.key === this.activeTab)
    },
    activeSymbols() {
      if (!this.activeKeyboardGroup) return []

      const symbols = this.activeKeyboardGroup.symbols
      if (this.activeTab !== 'cyrillic' || this.showUppercase) return symbols

      return symbols.filter(s => s !== s.toUpperCase())
    }
  },
  watch: {
    selectedFont(newFont, oldFont) {
      const fromDict = dictionaries[oldFont]
      const toDict = dictionaries[newFont]

      if (fromDict && toDict) {
        this.text = convertText(this.text, fromDict, toDict)
      }
    }
  },
  mounted() {
    document.addEventListener('keydown', this.handleKeydown)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
  },
  methods: {
    handleKeydown(e) {
      if (e.key === 'F1') {
        e.preventDefault()
        this.showHelpModal = true
      } else if (e.key === 'Escape') {
        this.showHelpModal = false
        this.showMarginsModal = false
        this.errorMessage = ''
      }
    },
    triggerFileImport() {
      this.$refs.fileInput.value = ''
      this.$refs.fileInput.click()
    },
    async handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return

      try {
        this.text = await importFile(file)
      } catch (error) {
        this.errorMessage = error.message || 'Ошибка загрузки файла'
      }
    },
    async compileText() {
      this.isCompiling = true
      this.errorMessage = ''
      try {
        const blob = await compileText(this.text, this.selectedFont, this.fontSize, this.margins)
        if (this.pdfUrl) {
          URL.revokeObjectURL(this.pdfUrl)
        }
        this.pdfUrl = URL.createObjectURL(blob)
      } catch (error) {
        this.errorMessage = 'Ошибка компиляции: ' + error.message
      } finally {
        this.isCompiling = false
      }
    },
    async exportPdf() {
      this.isExporting = true
      this.errorMessage = ''
      try {
        const blob = await exportPdf(this.text, this.selectedFont, this.fontSize, this.margins)
        downloadPdfBlob(blob)
      } catch (error) {
        this.errorMessage = 'Ошибка экспорта PDF: ' + error.message
      } finally {
        this.isExporting = false
      }
    },
    async exportDocx() {
      this.isExporting = true
      this.errorMessage = ''
      try {
        const blob = await exportDocx(this.text, this.selectedFont, this.fontSize, this.margins)
        downloadDocxBlob(blob)
      } catch (error) {
        this.errorMessage = 'Ошибка экспорта DOCX: ' + error.message
      } finally {
        this.isExporting = false
      }
    },
    convertToGlagolitic() {
      this.text = convertDirect(this.text, glagolitic.CyrillicToGlagolitic)
    },
    convertToCyrillic() {
      this.text = convertDirect(this.text, glagolitic.GlagoliticToCyrillic)
    },
    insertSymbol(symbol) {
      const textarea = this.$refs.textEditor
      const start = textarea.selectionStart
      const end = textarea.selectionEnd

      this.text = this.text.slice(0, start) + symbol + this.text.slice(end)

      this.$nextTick(() => {
        textarea.focus()
        textarea.selectionStart = textarea.selectionEnd = start + symbol.length
      })
    }
  },
}
</script>

<style scoped>
.editor-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: #f7f8fa;
  font-family: system-ui, -apple-system, sans-serif;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding: 10px 15px;
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
}

@media (max-width: 768px) {
  .toolbar {
    flex-wrap: nowrap;
    overflow-x: auto;
    gap: 4px;
    padding: 6px;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  .toolbar::-webkit-scrollbar {
    display: none;
  }
  .toolbar button,
  .toolbar select {
    flex-shrink: 0;
    padding: 4px 8px;
    font-size: 12px;
  }
  .toolbar label {
    font-size: 12px;
    flex-shrink: 0;
  }
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

.toolbar button:hover:not(:disabled) {
  background: #f0f0f0;
}

.toolbar button:active:not(:disabled) {
  transform: scale(0.97);
}

.toolbar button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.error-toast {
  position: fixed;
  bottom: 300px;
  left: 50%;
  transform: translateX(-50%);
  background: #d32f2f;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  cursor: pointer;
  z-index: 1000;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateX(-50%) translateY(20px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
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
  src: url('/fonts/BukyVede.ttf');
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
  src: url('/fonts/MenaionUnicode.otf');
}

@font-face {
  font-family: 'PonomarUnicode';
  src: url('/fonts/PonomarUnicode.otf');
}

.help-modal {
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.help-modal h3 {
  margin-bottom: 20px;
  color: #333;
}

.help-modal h4 {
  margin: 15px 0 10px 0;
  color: #4a90e2;
  font-size: 16px;
}

.help-section {
  margin-bottom: 15px;
}

.help-section ul {
  margin: 0;
  padding-left: 20px;
}

.help-section li {
  margin-bottom: 8px;
  line-height: 1.5;
  font-size: 14px;
}
</style>
