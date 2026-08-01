<template>
  <div>
    <h2>Participants for Trek {{ trekId }}</h2>
    <ul>
      <li v-for="p in participants" :key="p.id">
        {{ p.name }} - {{ p.email }} - Status: {{ p.status }}
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'Participants',
  props: ['trekId'],
  data() {
    return { participants: [] }
  },
  async mounted() {
    const token = localStorage.getItem('token')
    this.participants = (await axios.get(`http://127.0.0.1:5000/participants/${this.trekId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })).data
  }
}
</script>
