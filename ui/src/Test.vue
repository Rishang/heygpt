<template>
  <div id="app">
    <li v-for="item in info">
      <b @click="test(item.Command)">
        {{ item.Title }}
      </b>
    </li>
  </div>
</template>

<script>
import axios from "axios";

export default {
  el: "#app",
  data() {
    return {
      info: null,
    };
  },
  methods: {
    test(item) {
      console.log(item);
    }
  },
  mounted() {
    axios
      .get("http://localhost:5000/prompt-items")
      .then((response) => (this.info = response.data));
  },
};
</script>
