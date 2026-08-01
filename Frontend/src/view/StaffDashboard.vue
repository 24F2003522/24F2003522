<template>
  <div>
    <h2>Staff Dashboard</h2>
    <div v-for="t in treks" :key="t.id" class="trek-card">
      <p>
        <strong> {{ t.name }}</strong> - {{ t.location }}  
        | Slots: {{ t.slots }}  
        | Status: {{ t.status }}  
        | Registered Trekkers: {{ t.registered_count }}
      </p>

      <!-- Update slots -->
      <form @submit.prevent="updateTrek(t)">
        <label for="slots">Update Slots:</label>
        <input v-model.number="t.slots" type="number" id="slots" />
        <select v-model="t.status">
        <option>open</option>
        <option>closed</option>
        <option>started</option>
        <option>ongoing</option>
        <option>completed</option>
      </select>
        <button type="submit">Update Slots</button>
      </form>
     
      

      <!-- Link to participants page -->
      <router-link :to="`/participants/${t.id}`">View Participants</router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'StaffDashboard',
  data() {
    return { treks: [{ id: null, name: '', location: '', slots: 0, status: '', registered_count: 0  }] }
  },
  async mounted() {
    const token = localStorage.getItem('token')
    this.treks = (await axios.get('http://127.0.0.1:5000/staffDashboard', {
      headers: { Authorization: `Bearer ${token}` }
    })).data
  },
  methods: {
    async updateTrek(t) {
      
  const token = localStorage.getItem('token')
  const res = await axios.put(`http://127.0.0.1:5000/staff/updateTrek/${t.id}`, {
    slots: t.slots,
    status: t.status
    
  }, { headers: { Authorization: `Bearer ${token}` } })

   alert("Trek updated!")
  console.log("Updated trek:", res.data)

 
}


  }
}
</script>

<style>
.trek-card {
  border: 1px solid #ddd;        
  border-radius: 8px;             
  padding: 12px;                 
  margin: 10px 0;                 
  background-color: #f9f9f9;      
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
}
trek-card button {
  background-color: #0dcb13;      
  color: rgb(255, 255, 255);
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}


</style>