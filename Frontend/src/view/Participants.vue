<template>
  <h2>Participants for Trek ID: {{ trekId }}</h2>
  <h3 style=" text-align: right;" class="red"><router-link to="/staff">Back to Staff Dashboard</router-link></h3>
  <table>
    <thead>
      <tr>
        <th>Participant Name</th>
        <th>Participant Email</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="p in participants" :key="p.id">
        <td>{{ p.name }}</td>
        <td>{{ p.email }}</td>
        <td>{{ p.status }}</td>
      </tr>
    </tbody>
  </table>
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
