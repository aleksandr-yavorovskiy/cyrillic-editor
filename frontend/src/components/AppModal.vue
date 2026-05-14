<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal" :class="modalClass">
      <h3 v-if="title">{{ title }}</h3>
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    show: Boolean,
    title: String,
    modalClass: String,
  },
  emits: ['close'],
}
</script>

<style scoped>
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
  margin-bottom: 20px;
  color: #333;
}

.help-modal {
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}
</style>
