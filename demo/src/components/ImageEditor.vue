<template>
    <div>
        <div class="button-container">
          <i v-if="status === EditorStatus.Edit" class="iconfont icon-touming" @click="removebg"></i>
          <i v-if="status === EditorStatus.Edit" class="iconfont icon-shunshizhenxuanzhuan" @click="rotateImage"></i>
          <i v-if="status === EditorStatus.Edit" class="iconfont icon-clear"  @click="clear"></i>

          <i v-if="status === EditorStatus.Show" class="iconfont icon-fenxiang"  @click="sharePng"></i>
          <i v-if="status === EditorStatus.Show" class="iconfont icon-xiazai"  @click="downloadPng"></i>

          <i v-if="status === EditorStatus.Edit || status === EditorStatus.Show" class="iconfont icon-shanchu"  @click="deleteImage"></i>
        </div>          
        <img v-if="status === EditorStatus.Ready" src="@/assets/images/upload_image.png" @click="triggerInput" style="width: 700px;">
        <div v-if="imageBase64 && status !== EditorStatus.Ready" style="position: relative; width: 700px;">
            <img ref="displayImgRef" :src="imageBase64" style="width: 700px;" @load="syncCanvas">
            <DrawBoardCanvas ref="drawBoardRef" :width="editorSize.width" :height="editorSize.height"></DrawBoardCanvas>
        </div>    
        <input type="file" ref="fileInputRef" @change="handleFileChange" style="display: none;" accept="image/*">
        <canvas ref="fullImageRef" style="display: none;"></canvas>
    </div>
</template>
  
<script lang="ts" setup>
import { onMounted, reactive, ref, watch } from 'vue';
import DrawBoardCanvas from './DrawBoardCanvas.vue';

enum EditorStatus {
    Ready = 0,
    Edit = 1,
    Draw = 2,
    Show = 3
}

const imageBase64 = ref<string | null>(null);
const displayImgRef = ref<HTMLImageElement | null>(null);
const drawBoardRef = ref<InstanceType<typeof DrawBoardCanvas> | null>(null);
const fullImageRef = ref<HTMLCanvasElement | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const status = ref<EditorStatus>(EditorStatus.Ready);
const editorSize = reactive<{width: number, height: number}>({width: 700, height: 500})

const syncCanvas = () => {
    if (displayImgRef.value) {
        editorSize.width = displayImgRef.value.width
        editorSize.height = displayImgRef.value.height
    }
    console.log(">>>do syncCanvas: " + editorSize.width + "," + editorSize.height)
}

const triggerInput = () => {
    fileInputRef.value?.click();
}

const handleFileChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
        console.log(">>> upload fiel: " + file.name)
        const reader = new FileReader();
        reader.onload = (e) => {
        imageBase64.value = e.target?.result as string;
        drawImage();
        };
        reader.readAsDataURL(file);
        status.value = EditorStatus.Edit;
    }
}

const drawImage = () => {
    if (imageBase64.value === null || fullImageRef.value === null) {
        return;
    }
    const canvas = fullImageRef.value;
    const ctx = canvas.getContext('2d');
    if (ctx === null) {
        return;
    }
    const img = new Image();
    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0, img.width, img.height);
    };
    img.src = imageBase64.value;
}

const deleteImage = () => {
    imageBase64.value = null;
    status.value = EditorStatus.Ready;
    if (fullImageRef.value) {
        const canvas = fullImageRef.value;
        const ctx = canvas.getContext('2d');
        ctx?.clearRect(0, 0, canvas.width, canvas.height);
    }
}

const rotateImage = () => {
    if (fullImageRef.value === null) {
        return;
    }
    const canvas = fullImageRef.value;
    const ctx = canvas.getContext('2d');
    if (ctx === null) {
        return;
    }
    const img = new Image();
    img.src = canvas.toDataURL();
    img.onload = () => {
        const originalWidth = img.width;
        const originalHeight = img.height;
        canvas.width = originalHeight;
        canvas.height = originalWidth;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate((90 * Math.PI) / 180);
        ctx.drawImage(img, -originalWidth / 2, -originalHeight / 2);
        ctx.rotate((-90 * Math.PI) / 180);
        ctx.translate(-canvas.width / 2, -canvas.height / 2);
        imageBase64.value = canvas.toDataURL();
    };
}

const clear = () => {
    drawBoardRef.value?.cancel();
}

const removebg = () => {
    const polygonPoints = drawBoardRef.value?.confirm() || []
    const points:Array<Array<number>> = []
    polygonPoints.forEach(point => {
        points.push([point.x, point.y])
    })
    const payload = {
        base64: imageBase64.value,
        selectPolygon: points,
        editorSize: [editorSize.width, editorSize.height],
        responseFormat: 0
    }
    fetch('/removebg', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(resp => {
        if(resp.status == 200){
            resp.json().then(apiResult => {
                if(apiResult.code != 0){
                    alert(apiResult.msg)
                }
                else{
                    imageBase64.value = apiResult.result
                    status.value = EditorStatus.Show
                }
            })
        }
        else{
            console.error(resp.status + ":" + resp.statusText)
        }
    })
    .catch(error => {
        console.log(error)
    })
}

const downloadPng = () => {
    // TODO: 实现下载PNG功能
}

const sharePng = () => {
    // TODO: 实现分享PNG功能
}
  
onMounted(() => {
    if (displayImgRef.value?.complete) {
      syncCanvas();
    }
});
  
watch(status, (newStatus) => {
    if (newStatus === EditorStatus.Ready && displayImgRef.value) {
      syncCanvas();
    }
});
</script>
  
<style lang="css" scoped>
img {
  user-select: none; /* 禁用用户选择 */
  -webkit-user-drag: none; /* 禁用图像拖动 */
}

.iconfont {
    font-size: 16px;
    color: #18c064;
}

.button-container {
    top: 10px;
    left: 10px;
    display: flex;
    justify-content: flex-end;
    gap: 10px; /* 按钮之间的间距 */
}

.button-container i {
    cursor: pointer;
}
</style>
  