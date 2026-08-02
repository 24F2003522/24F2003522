<template>
  <div>
    <h2>User Dashboard</h2>
    <p v-if="message" style="color:red">{{ message }}</p>

    <h3>Search & Filter Treks</h3>
    <input v-model="searchQuery" placeholder="Search by name or location" />
    <select v-model="filterDifficulty">
      <option value="">All Difficulties</option>
      <option value="easy">Easy</option>
      <option value="medium">Medium</option>
      <option value="hard">Hard</option>
    </select>
    <button @click="loadTreks">Apply Filters</button>

    <h3>Available Treks</h3>
    <div v-for="t in treks" :key="t.id" class="trek-card">
      <p>
        <strong>{{ t.name }}</strong> - {{ t.location }}
        | Difficulty: {{ t.difficulty }}
        | Slots: {{ t.slots }}
        | Status: {{ t.status }}
      </p>
      <button  @click="bookTrek(t.id)">
        Book Trek
      </button>

      
    </div>
    <router-link to="/booking-history">View Booking & Trekking History</router-link>


  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'Trekkers',
  data() {
    return {
      treks: [],
      bookings: [],
      history: [],
      searchQuery: '',
      filterDifficulty: '',
      message: ''
    }
  },
  async mounted() {
    await this.loadTreks()

  },
  methods: {
    async loadTreks() {
      // alert("Loading treks...")
      const token = localStorage.getItem('token')
      console.log("Token:", token)
      try {
        const res = await axios.get('http://127.0.0.1:5000/user/allTreks', {
          params: { q: this.searchQuery, difficulty: this.filterDifficulty },
          headers: { Authorization: `Bearer ${token}` }
        })
        this.treks = res.data.filter(t => t.status === 'open' && t.slots > 0)
      } catch (err) {
        this.message = 'Failed to load treks'
      }
    },
    async bookTrek(trekId) {
      const token = localStorage.getItem('token')
      try {
        await axios.post(`http://127.0.0.1:5000/user/book/${trekId}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
        alert("Booking successful!")
        const trek = this.treks.find(t => t.id === trekId)
        
      } catch (err) {

        alert(err?.response?.data?.message || 'Booking failed')
      }
    },

      
    }
  }


</script>

<style>
.trek-card,
.booking-card,
.history-card {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 10px;
  margin: 8px 0;
  background: #f9f9f9;
}

button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
