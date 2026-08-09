<template class="dashboard">
    <Navbar />
    <h1>Admin Dashboard</h1>
    <h3 style="text-align: right;" class="red">
        <button @click="logout">Logout</button>
    </h3>
    <p v-if="message" style="color: red;">{{ message }}</p>
    <h3>Total Treks: {{ stats.treks }}</h3>
    <h3>Total Users: {{ stats.users }}</h3>
    <h3>Total Staff: {{ stats.staff }}</h3>
    <h3>Total Bookings: {{ stats.bookings }}</h3>
    <h3 style=" text-align: left;" class="blue"><router-link to="/bookings">View Bookings</router-link></h3>
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
    <div>
        <h2>Add New Trek</h2>
        <form @submit.prevent="addTrek">
            <input v-model="newTrek.name" placeholder="Trek Name" required />
            <input v-model="newTrek.location" placeholder="Location" required />
            <input v-model="newTrek.slots" type="number" placeholder="Slots" required />
            <input v-model="newTrek.start_date" type="date" placeholder="Start Date" required />
            <input v-model="newTrek.end_date" type="date" placeholder="End Date" required />
            <select v-model="newTrek.status">
                <option>open</option>
                <option>pending</option>
                <option>approved</option>
                <option>completed</option>
            </select>
            <select v-model="newTrek.difficulty">
                <option>easy</option>
                <option>medium</option>
                <option>hard</option>
            </select>
            <button type="submit">Add Trek</button>
        </form>
        <h3 style=" text-align: left;" class="red"><router-link to="/assign-staff">Assign Staff</router-link></h3>
    </div>
    <h2>Manage Trek</h2>
    <div class="scroll">
        <p v-for="trek in trek" :key="trek.id">
            <!-- <p>{{ trek.name }} - {{ trek.location }} - Slots: {{ trek.slots }}</p>
            <button @click="deleteTrek(trek.id)">Delete</button>
            <button @click="editTrek(trek.id)">Edit</button> -->
            <input v-model="trek.name" />
            <input v-model="trek.location" />
            <input v-model.number="trek.slots" type="number" />
            <select v-model="trek.status">
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="pending">Pending</option>
                <option valur="approved">Approved</option>
                <option value="completed">Completed</option>
            </select>
            <select v-model="trek.difficulty">
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
            </select>
            <select v-model="trek.staff_id">
                <option value="">None</option>
                <option v-for="s in staff" :key="s.id" :value="s.id">
                    {{ s.name }}
                </option>
            </select>
            <button @click="deleteTrek(trek.id)">Delete</button>
            <button @click="editTrek(trek)">Save Changes</button>

        </p>
    </div>
    <h2>Add New Staff</h2>
    <form @submit.prevent="addStaff">
        <input v-model="newStaff.name" placeholder="Staff Name" required />
        <input v-model="newStaff.email" type="email" placeholder="Email" required />
        <input v-model="newStaff.password" type="password" placeholder="Password" required />
        <button type="submit">Add Staff</button>
    </form>
    <h2>Manage Users and Staff</h2>
    <div class="scroll">

        <p v-for="user in user" :key="user.id">

            <input v-model="user.name" />
            <input v-model="user.email" />
            <select v-model="user.status">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
            </select>

            <button @click="deleteUser(user.id)">Delete</button>
            <button @click="editUser(user)">Save Changes</button>
        </p>
    </div>


</template>
<script>
import Navbar from '../components/Navbar.vue'
import axios from 'axios'
export default {
    name: 'Admin', components: { Navbar },
    data() {
        return {
            stats: {}, newTrek: {}, newStaff: {}, message: '', trek: [], user: [],
            searchQuery: '', searchResults: null
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
            this.staff = (await axios.get('http://127.0.0.1:5000/allStaff', { headers: { Authorization: `Bearer ${token}` } })).data

        } catch (error) {
            console.error('Admin dashboard error:', error)
            this.message = error?.response?.data?.message || 'Failed to load dashboard data.'
        }
    },
    methods: {
        async addTrek() {
            try {
                await axios.post('http://127.0.0.1:5000/creatTrek', this.newTrek, {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                })
                alert("Trek created!")
                this.newTrek = { name: '', location: '', slots: '' }
                const token = localStorage.getItem('token');
                const trekRes = await axios.get('http://127.0.0.1:5000/allTreks', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.trek = trekRes.data

            }
            catch (error) {
                console.error('Error creating trek:', error)
                this.message = error?.response?.data?.message || 'Failed to create trek.'
                alert(this.message)
                this.message = ''
            }
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
                location: trek.location, staff_id: trek.staff_id,
                slots: trek.slots, status: trek.status, difficulty: trek.difficulty
            }, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            alert("Trek updated!")
        },
        async addStaff() {
            try {
                const token = localStorage.getItem('token')
                await axios.post('http://127.0.0.1:5000/addStaff', this.newStaff, {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                })
                alert("Staff added!")
                //this.user.push(response.data);
                const userRes = await axios.get('http://127.0.0.1:5000/allUsers', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.user = userRes.data
                this.newStaff = { name: '', email: '', password: '' }
            } catch (error) {
                console.error('Error adding staff:', error)
                this.message = error?.response?.data?.message || 'Failed to add staff.'
                alert(this.message)
                this.message = ''
            }
        },
        async editUser(user) {
            alert("Editing user with ID: " + user.id)
            await axios.put(`http://127.0.0.1:5000/updateUser/${user.id}`, {
                name: user.name,
                email: user.email,
                status: user.status,

            }, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            alert("User updated!")
        },
        async deleteUser(id) {
            await axios.delete(`http://127.0.0.1:5000/deleteUser/${id}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            })
            alert("User deleted!")
            this.user = this.user.filter(u => u.id !== id)
        },
        async searchData() {
            const token = localStorage.getItem('token')
            try {
                const response = await axios.get(`http://127.0.0.1:5000/search`, {
                    params: { q: this.searchQuery },
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.searchResults = response.data
                this.trek = this.searchResults.treks
                this.user = this.searchResults.users
            } catch (error) {
                console.error('Search error:', error)
                this.message = error?.response?.data?.message || 'Failed to search.'
            }
        },

        logout() {
            localStorage.removeItem('token')
            localStorage.removeItem('role')
            this.$router.push('/')
            alert("You have been logged out successfully!")
        }
    }
}

</script>
<style>
.scroll {
    max-height: 300px;
    overflow-y: auto;
}
</style>