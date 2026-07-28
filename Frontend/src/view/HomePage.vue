<template>
    <div>   
        Home Page
        <div><router-link to="/login">Login</router-link></div>
        <div><router-link to="/register">Register</router-link></div>
    </div>
</template>

<script>
    export default {
        name: 'Home',
        data() {
            return {
                message: 'Welcome to the Home Page!'
            }
        }
    }
</script>