import axios from 'axios'

const axiosInstance = axios.create({
    timeout: 10000,
    validateStatus: function (status) {
      return true
    }
  })


export default axiosInstance