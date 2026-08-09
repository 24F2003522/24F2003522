<template>
  <Navbar />
  <h1>User Dashboard</h1>
  <h3 style="text-align: right;" class="red">
    <button @click="logout">Logout</button>
  </h3>
  <h2>Welcome, {{ userName }}</h2>
  <button @click="exportHistory">Export Trekking History (CSV)</button>
  <p>{{ exportMessage }}</p>
  <h3 style=" text-align: left;" class="red"> <router-link to="/edit-user">Edit Profile</router-link></h3>
  <div>
    <h2>Search & Filter Treks</h2>
    <input v-model="searchQuery" placeholder="Search by name or location" />
    <select v-model="filterDifficulty">
      <option value="">All Difficulties</option>
      <option value="easy">Easy</option>
      <option value="medium">Medium</option>
      <option value="hard">Hard</option>
    </select>
    <button @click="loadTreks">Apply Filters</button>
    <h2>Available Treks</h2>
    <div v-for="t in treks" :key="t.id" class="trek-card">

      <strong>{{ t.name }}</strong> - {{ t.location }}
      | Difficulty: {{ t.difficulty }}
      | Slots: {{ t.slots }}
      | Status: {{ t.status }}|Assign Staff :{{ t.staff_name }}

      <button @click="bookTrek(t.id)">
        Book Trek
      </button>
    </div>
  </div>
  <h3 style=" text-align: left;" class="blue">
    <router-link to="/booking-history">View Booking & Trekking History</router-link>
  </h3>
</template>

<script>
import Navbar from '../components/Navbar.vue'
import axios from 'axios'
export default {
  name: 'Trekkers', components: { Navbar },
  data() {
    return {
      treks: [], userName: '', bookings: [],
      history: [], searchQuery: '', filterDifficulty: '', message: ''
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
        this.userName = res.data.user_name
        this.treks = res.data.treks.filter(t => t.status === 'open' && t.slots > 0)
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
        this.treks = this.treks.filter(t => t.id !== trekId)
      } catch (err) {

        alert(err?.response?.data?.message || 'Booking failed')
      }
    },

    logout() {
      localStorage.removeItem('token')
      this.$router.push('/')
      alert("You have been logged out successfully!")
    },

    async exportHistory() {
      const token = localStorage.getItem('token')
      try {
        const res = await axios.post('http://127.0.0.1:5000/user/exportHistory', {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.exportMessage = "Export started. Task ID: " + res.data.task_id
        this.checkExportStatus(res.data.task_id)
      } catch (err) {
        this.exportMessage = 'Failed to start export'
      }
    },
    async checkExportStatus(taskId) {
      const token = localStorage.getItem('token')
      const interval = setInterval(async () => {
        try {
          const res = await axios.get(`http://127.0.0.1:5000/task/${taskId}`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          if (res.data.status === "SUCCESS") {
            clearInterval(interval)
            this.exportMessage = "Export complete! Download link ready."
            this.downloadCSV(res.data.result)
          }
        } catch (err) {
          clearInterval(interval)
          this.exportMessage = "Error checking export status"
        }
      }, 3000)
      alert("Export Started >>> Wait !")
    }, async downloadCSV(filePath) {
      const token = localStorage.getItem('token')
      try {
        const res = await axios.get(`http://127.0.0.1:5000/download/${filePath}`, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        })

        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filePath.split('/').pop())
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (err) {
        this.exportMessage = "Failed to download CSV"
      } alert("Finish")
    }
  }
}
</script>

<style>
div {
  max-width: 10000px;
  margin: 30px auto;
  padding: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);

  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

}

input,
select {
  padding: 8px;
  margin: 6px 10px 12px 0;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input:focus,
select:focus {
  border-color: #4CAF50;
  outline: none;
}

.trek-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin: 12px 0;
  background: #f9f9f9;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.trek-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

button:hover {
  background: #45a049;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

a {
  display: inline-block;
  margin-top: 20px;
  color: #4CAF50;
  text-decoration: none;
  font-weight: bold;
}

a:hover {
  text-decoration: underline;
}
</style>
