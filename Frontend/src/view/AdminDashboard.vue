<template>
    <div>
        <h2>Admin Dashboard</h2>
        <p v-if="message" style="color: red;">{{ message }}</p>
        <p>Total Treks: {{ stats.treks }}</p>
        <p>Total Users: {{ stats.users }}</p>
        <p>Total Staff: {{ stats.staff }}</p>
        <p>Total Bookings: {{ stats.bookings }}</p>
        <h3>Search</h3>
        <input v-model="searchQuery" placeholder="Search by name or ID" />
        <button @click="searchData">Search</button>

        <div v-if="searchResults">
            <h4>Treks</h4>
            {{ searchResults.treks.length === 0 ? 'No treks found.' : '' }}
            <div v-for="t in searchResults.treks" :key="t.id">
                {{ t.name }} - {{ t.location }}
            </div>

            <h4>Users</h4>
            {{ searchResults.users.length === 0 ? 'No users found.' : '' }}
            <div v-for="u in searchResults.users" :key="u.id">
                {{ u.name }} - {{ u.email }} - {{ u.role }}
            </div>


        </div>

        <h3>Add New Trek</h3>
        <form @submit.prevent="addTrek">
            <input v-model="newTrek.name" placeholder="Trek Name" required />
            <input v-model="newTrek.location" placeholder="Location" required />
            <input v-model="newTrek.slots" type="number" placeholder="Slots" required />
            <button type="submit">Add Trek</button>
        </form>
        <h3>Manage Trek</h3>
        <div v-for="trek in trek" :key="trek.id">
            <!-- <p>{{ trek.name }} - {{ trek.location }} - Slots: {{ trek.slots }}</p>
            <button @click="deleteTrek(trek.id)">Delete</button>
            <button @click="editTrek(trek.id)">Edit</button> -->
            <input v-model="trek.name" placeholder={{ trek.name }} />
            <input v-model="trek.location" placeholder={{ trek.location }} />
            <input v-model.number="trek.slots" type="number" placeholder={{ trek.slots }} />

            <button @click="deleteTrek(trek.id)">Delete</button>
            <button @click="editTrek(trek)">Save Changes</button>
        </div>
        <h3>Add New Staff</h3>
        <form @submit.prevent="addStaff">
            <input v-model="newStaff.name" placeholder="Staff Name" required />
            <input v-model="newStaff.email" type="email" placeholder="Email" required />
            <input v-model="newStaff.password" type="password" placeholder="Password" required />
            <button type="submit">Add Staff</button>
        </form>
        <h3>Manage Users and Staff</h3>
        <div v-for="user in user" :key="user.id">

            <input v-model="user.name" placeholder={{ user.name }} />
            <input v-model="user.email" placeholder={{ user.email }} />
            <input v-model="user.status" placeholder={{ user.status }} />

            <button @click="deleteUser(user.id)">Delete</button>
            <button @click="editUser(user)">Save Changes</button>
        </div>
        <router-link to="/assign-staff">Assign Staff</router-link>
        <div><router-link to="/bookings">Bookings</router-link></div>
        
        

    </div>
</template>
<script>
import axios from 'axios'
export default {
    name: 'Admin',
    data() {
        return {
            stats: { treks: 0, users: 0, staff: 0, bookings: 0 },
            newTrek: { name: '', location: '', slots: 0 },
            newStaff: { name: '', email: '', password: '' },
            message: '',
            trek: [], user: [],
            searchQuery: '',
            searchResults: null
        }
    },
    async mounted() {
        try {
            const token = localStorage.getItem('token')


            const response = await axios.get('http://127.0.0.1:5000/adminDashboard', {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            this.stats = response.data
            console.log('Admin dashboard data:', response.data)

            const trekRes = await axios.get('http://127.0.0.1:5000/allTreks', {
                headers: { Authorization: `Bearer ${token}` }
            })
            this.trek = trekRes.data

            const userRes = await axios.get('http://127.0.0.1:5000/allUsers', {
                headers: { Authorization: `Bearer ${token}` }
            })
            this.user = userRes.data

        } catch (error) {
            console.error('Admin dashboard error:', error)
            this.message = error?.response?.data?.message || 'Failed to load dashboard data.'
        }
    },
    methods: {
        async addTrek() {
            await axios.post('http://127.0.0.1:5000/creatTrek', this.newTrek, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            alert("Trek created!")
        },
        async deleteTrek(id) {
            await axios.delete(`http://127.0.0.1:5000/deleteTrek/${id}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            alert("Trek deleted!")

            this.trek = this.trek.filter(t => t.id !== id)
        },
        async editTrek(trek) {

            await axios.put(`http://127.0.0.1:5000/updateTrek/${trek.id}`, {
                name: trek.name,
                location: trek.location,
                slots: trek.slots
            }, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            alert("Trek updated!")
        },
        async addStaff() {
            await axios.post('http://127.0.0.1:5000/addStaff', this.newStaff, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            alert("Staff added!")
        },
        async editUser(user) {
            await axios.put(`http://127.0.0.1:5000/updateUser/${user.id}`, {
                name: user.name,
                email: user.email,
                status: user.status
            }, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            alert("User updated!")
        },
        async searchData() {
            const token = localStorage.getItem('token')
            try {
                const response = await axios.get(`http://127.0.0.1:5000/search`, {
                    params: { q: this.searchQuery },
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.searchResults = response.data
            } catch (error) {
                console.error('Search error:', error)
                this.message = error?.response?.data?.message || 'Failed to search.'
            }
        }
    }
}

</script>