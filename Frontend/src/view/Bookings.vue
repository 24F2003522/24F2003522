<template>
  <div>
    <h2>All Booking Records</h2>
    <table>
      <tr>
        <th>User</th><th>Trek</th><th>Date</th><th>Status</th>
      </tr>
      <tr v-for="b in bookings" :key="b.id">
        <td>{{ b.user_name }}</td>
        <td>{{ b.trek_name }}</td>
        <td>{{ b.date }}</td>
        <td>{{ b.status }}</td>
      </tr>
    </table>
    <div><router-link to="/admin">Admin Dashboard</router-link></div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
    name: 'Bookings',
  data() { return { bookings: [] } },
  async mounted() {
    const token = localStorage.getItem('token')
    this.bookings = (await axios.get('http://127.0.0.1:5000/allBookings', { headers: { Authorization: `Bearer ${token}` } })).data
  }
}
</script>
