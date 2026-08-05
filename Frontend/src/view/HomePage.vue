<template >

    <h1>Trekking Management Application</h1>
    <div style="text-align: center ;width: 50%; margin: 10px auto;" class="trek-card" >
        <h2 Style="color:">Welcome to the Trekking Management Application!</h2></br>
        One stop solution for all your trekking needs. Whether you're a trekker, staff, or admin, our application provides a seamless experience for managing treks, bookings, and user profiles.
    </div>
    <h3 class="red"><router-link to="/login">Login</router-link></h3>
    <h2 class="blue"><router-link to="/register">Register</router-link></h2>


</template>

<script>
export default {
    name: 'Home',
    data() {
        return {
            message: 'Welcome to the Trekking Management Application!'
        }
    }
}
</script>
<style>

h1 {
    color: #2c3e50;
    text-align: center;
    text-decoration: underline;
}

.red {
    
    text-align: center;
    margin-top: 20px;
    

}

.blue {
    
    text-align: center;
    margin-top: 20px;

}

.red a {
    color: hsl(0, 22%, 95%);
    background-color: #ac2f21;
    border-radius: 6px;
    padding: 10px 20px;
} 
.blue a {
    color: hsl(0, 22%, 95%);
    background-color: #1a73e8;
    border-radius: 6px;
    padding: 10px 20px;
}

</style>