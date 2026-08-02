<template>
    <div class="login">
        <h2>Login</h2>
        <form @submit.prevent="login">
            <div>
                <label for="email">Email:</label>
                <input type="email" v-model="email" required />
            </div>
            <div>
                <label for="password">Password:</label>
                <input type="password" v-model="password" required />
            </div>
            <button type="submit">Login</button>
        </form>
        <p>{{ message }}</p>
    </div>
</template>
<script>
import axios from 'axios'

export default {
    name: 'Login',
    data() {
        return {
            email: '',
            password: '',
            message: ''
        }
    },
    methods: {
        async login() {
            try {
                const response = await axios.post('http://127.0.0.1:5000/login', {
                    email: this.email,
                    password: this.password
                })
                console.log('Login successful');
                this.message = response?.data?.message || 'Login successful'
                localStorage.setItem('token', response?.data?.token)
                if (response?.data?.role === 'admin') {
                    this.$router.push('/admin') // vue page not python 
                } else if (response?.data?.role === 'staff' && response?.data?.status === 'active') {
                    this.$router.push('/staff')
                } else if (response?.data?.role === 'user' && response?.data?.status === 'active') {
                    this.$router.push('/trekkers')
                }
                else {
                    this.message = 'Your account is inactive. Please contact the administrator.'
                }
            } catch (error) {
                this.message = error?.response?.data?.message || 'Login failed'
            }
        }
    }
}
</script>

<style>
</style>