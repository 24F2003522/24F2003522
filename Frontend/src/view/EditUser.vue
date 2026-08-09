<template>
    <div>
        <h1> User Profile </h1>
        <h3 style=" text-align: right;" class="red"><router-link to="/trekkers">Dashboard</router-link></h3>
        <form @submit.prevent="updateUser">
            <div>
                <label for="name">Name:</label>
                <input type="text" v-model="user.name" />
            </div>
            <div>
                <label for="email">Email:</label>
                <input type="email" v-model="user.email" required />
            </div>
            <div>
                <label for="password">Password:</label>
                <input type="password" v-model="user.password" required />
            </div>
            <button type="submit">Save Changes</button>
        </form>
    </div>
</template>
<script>
import axios from 'axios';
export default {
    name: 'EditUser',
    data() {
        return {
            user: { name: '', email: '', password: '' },
            message: ''
        }
    },
    async mounted() {
        await this.loadUser()
    },
    methods: {
        async loadUser() {
            const token = localStorage.getItem('token')
            try {
                const res = await axios.get('http://127.0.0.1:5000/user/profile', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.user = res.data
            } catch (err) {
                this.message = err?.response?.data?.message || 'Failed to load user profile'
                alert(this.message)
            }
        },
        async updateUser() {
            const token = localStorage.getItem('token')
            try {
                await axios.put('http://127.0.0.1:5000/user/profile/edit', this.user, {
                    headers: { Authorization: `Bearer ${token}` }
                })
                alert('User profile updated successfully!')
            } catch (err) {
                this.message = err?.response?.data?.message || 'Failed to update user profile'
                alert(this.message)
            }
        }
    }
}
</script>
