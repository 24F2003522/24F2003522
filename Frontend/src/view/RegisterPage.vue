<template>
    <div class="register">
        <h2>Register</h2>
        <form @submit.prevent="register">
            <div>
                <label for="name">Name:</label>
                <input type="text" v-model="name" required />
            </div>
            <div>
                <label for="email">Email:</label>
                <input type="email" v-model="email" required />
            </div>
            <div>
                <label for="password">Password:</label>
                <input type="password" v-model="password" required />
            </div>
            <button type="submit">Register</button>
        </form>
        <p>{{ message }}</p>
    </div>
</template>
<script>
import axios from 'axios'

export default {
    name: 'Register',
    data() {
        return {
            name: '',
            email: '',
            password: '',
            message: ''
        }
    },
    methods: {
        async register() {
            try {
                const response = await axios.post('http://127.0.0.1:5000/register', {
                    name: this.name,
                    email: this.email,
                    password: this.password
                })
                console.log('Registration successful');
                this.message = response?.data?.message || 'Registration successful'
            } catch (error) {
                this.message = error?.response?.data?.message || 'Registration failed'
            }
        }
    }
}
</script>


<style lang="scss" scoped>

</style>