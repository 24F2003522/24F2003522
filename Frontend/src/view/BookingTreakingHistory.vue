<template>
   
        <h1>Booking</h1>
        <h3 style=" text-align: right;" class="red"><router-link to="/trekkers">Dashboard</router-link></h3>
        <div v-if="bookings.length === 0">
            <p>No booking history available.</p>
        </div>
        <div v-else>
            <table>
                <thead>
                    <tr>
                        <th>Trek Name</th>
                        <th>Location</th>
                        <th>Status</th>
                        <th>Trekking Status</th>
                        <th>Cancel</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="booking in bookings" :key="booking.id">
                        <td>{{ booking.trek_name }}</td>
                        <td>{{ booking.location }}</td>
                        <td>{{ booking.status }}</td>
                        <td>{{ booking.treakingStatus }}</td>
                        <td>
                            <button @click="cancelBooking(booking.id)">
                                Cancel
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <h1>Trekking History</h1>
        <div v-if="history.length === 0">
            <p>No trekking history available.</p>
        </div>
        <div v-else>
            <table>
                <thead>
                    <tr>
                        <th>Trek Name</th>
                        <th>Location</th>
                        <th>Status</th>

                    </tr>
                </thead>
                <tbody>
                    <tr v-for="booking in history" :key="booking.id">
                        <td>{{ booking.trek_name }}</td>
                        <td>{{ booking.location }}</td>
                        <td v-if="booking.status === 'cancel'">{{ booking.status }}</td>
                        <td v-else>{{ booking.treakingStatus }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
   
</template>
<script>
import axios from 'axios'
export default {
    name: "BookingTrackingHistory",
    data() {
        return {
            bookings: [],
            history: [],
            message: ''
        }
    },
    async mounted() {
        const token = localStorage.getItem('token')
        try {
            const res = await axios.get('http://127.0.0.1:5000/user/bookings', {
                headers: { Authorization: `Bearer ${token}` }
            })


            this.bookings = res.data
            const bookingRes = await axios.get('http://127.0.0.1:5000/user/history', {
                headers: { Authorization: `Bearer ${token}` }
            })
            this.history = bookingRes.data
            console.log('Booking history:', this.history)
            // alert("Booking history loaded successfully!")
        } catch (error) {
            this.message = error?.response?.data?.message || 'Failed to load booking history.'
        }
    },
    methods: {
        async cancelBooking(bookingId) {
            alert(bookingId)
            const token = localStorage.getItem('token')

            await axios.post(`http://127.0.0.1:5000/user/cancel/${bookingId}`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            })
            alert("Cancellation successful!")

            // Update local state immediately
            const booking = this.bookings.find(b => b.id === bookingId)
            if (booking) {
                booking.status = "cancel"

                this.history.push(booking)
                this.bookings = this.bookings.filter(b => b.id !== bookingId)
            }
        }
    }
}

</script>
<style>
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 16px;
    text-align: left;
}

thead {
    background-color: #4CAF50;
    color: white;
}

th,
td {
    padding: 12px 15px;
    border: 1px solid #ddd;
}



h1 {
    margin-top: 30px;
    color: #333;
}

p {
    font-style: italic;
    color: #666;
}

div {
    margin-bottom: 20px;
}
</style>