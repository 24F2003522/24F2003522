<template>

    <h2>Assign Staff to Treks</h2>
    <h3 style=" text-align: right;" class="red"><router-link to="/admin">Admin Dashboard</router-link></h3> 
    
    <div v-for="trek in treks" :key="trek.id" class="trek-item">
  <h3>
    Trek Name: {{ trek.name }} || Location: {{ trek.location }} ||
    Assigned Staff: {{ trek.staff_name ? trek.staff_name : 'None' }}
  </h3>
  <select v-model="selectedStaff[trek.id]">
    <option v-for="s in staff" :key="s.id" :value="s.id">
      {{ s.name }}
    </option>
  </select>
  <button @click="assignStaff(trek.id)">Assign</button>
</div>

   
</template>

<script>
import axios from 'axios'
export default {
    name: 'AssignStaff',
  data() {
    return { treks: [], staff: [], selectedStaff: {} }
  },
  async mounted() {
    const token = localStorage.getItem('token')
    this.treks = (await axios.get('http://127.0.0.1:5000/allTreks', { headers: { Authorization: `Bearer ${token}` } })).data
    this.staff = (await axios.get('http://127.0.0.1:5000/allStaff', { headers: { Authorization: `Bearer ${token}` } })).data
    this.treks.forEach(t => {
    this.selectedStaff[t.id] = t.staff_id || "";
    })
    // alert(this.treks)
    // alert(this.selectedStaff)
  },
  methods: {
    async assignStaff(trekId) {
      const staffId = this.selectedStaff[trekId]
      await axios.put(`http://127.0.0.1:5000/assignStaff/${trekId}/${staffId}`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      alert("Staff assigned!")
      
    }
  }
}
</script>
