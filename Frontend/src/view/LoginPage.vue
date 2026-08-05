<template>
    <div class="start">
        <h1>Login</h1>
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
    <router-link to="/register">Don't have an account? Register here</router-link>
    </div>
</template>
<script>
import axios from 'axios'
import router from '../main';

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
                    alert("Welcome Admin")
                    this.$router.push('/admin') // vue page not python 
                } else if (response?.data?.role === 'staff' && response?.data?.status === 'active') {
                 this.$router.push('/staff')
                    alert("Welcome "+response?.data.name)
                } else if (response?.data?.role === 'user' && response?.data?.status === 'active') {
                    this.$router.push('/trekkers')
                    alert("Welcome "+response?.data.name)
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
<style >
.start {
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    text-align: center;
}
</style>
