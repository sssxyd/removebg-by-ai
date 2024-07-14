<script setup lang="ts">
import ImageEditor from '@/components/ImageEditor.vue'
</script>

<template>
<div id="content">
  <div class="header">
    <span style="font-size: 24px; padding-left: 80px;">RemoveBG By AI Model</span>
    <span style="padding-top: 8px; padding-left: 5px;"><iframe src="https://ghbtns.com/github-btn.html?user=sssxyd&repo=removebg-by-ai&type=star&size=large&text=false" frameborder="0" scrolling="0" width="170" height="30" title="GitHub"></iframe></span>
  </div>
  <ImageEditor/>
  
</div>
</template>

<style scoped>
#content {
  position: relative;
  flex-direction: column;
}
.header {
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center;    /* 垂直居中 */
  flex-direction: row;    /* 默认是row，可以省略 */
}

</style>
