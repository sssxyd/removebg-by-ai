<template>
    <div class="editor-container">
        <div class="button-container">
          <i v-if="status === EditorStatus.Edit" class="iconfont icon-touming" @click="removebg"></i>
          <i v-if="status === EditorStatus.Edit" class="iconfont icon-shunshizhenxuanzhuan" @click="rotateImage"></i>
          <i v-if="status === EditorStatus.Edit" class="iconfont icon-clear" @click="clear"></i>

          <i v-if="status === EditorStatus.Show" class="iconfont icon-fenxiang" @click="sharePng"></i> 
          <i v-if="status === EditorStatus.Show" class="iconfont icon-xiazai" @click="downloadPng"></i>

          <i v-if="status === EditorStatus.Edit || status === EditorStatus.Show" class="iconfont icon-shanchu" @click="deleteImage"></i>
        </div>       
           
        <img v-if="status === EditorStatus.Ready" src="@/assets/images/upload_image.png" @click="showModal">
        <div v-if="imageBase64 && status !== EditorStatus.Ready" class="canvas-container">
            <img ref="displayImgRef" :src="imageBase64" @load="syncCanvas">
            <DrawRectCanvas ref="drawBoardRef" :width="editorSize.width" :height="editorSize.height"></DrawRectCanvas>
        </div>    
        <input type="file" ref="fileInputRef" @change="handleFileChange" style="display: none;" accept="image/*">
        <canvas ref="fullImageRef" style="display: none;"></canvas>

        <!-- Modal for load options -->
        <div v-if="showLoadOptionModal" class="modal">
            <div class="modal-content">
                <h3>Load Image</h3>
                <button @click="triggerInput">Load from Local</button>
                <div class="url-input-container">
                    <input 
                        v-model="imageUrlInput" 
                        type="text" 
                        placeholder="Enter image URL"
                        @keyup.enter="loadImageFromUrl"
                    >
                    <button @click="loadImageFromUrl">Load from URL</button>
                </div>
                <button @click="closeModal">Cancel</button>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref, watch } from 'vue';
import DrawRectCanvas from './DrawRectCanvas.vue';

enum EditorStatus {
    Ready = 0,
    Edit = 1,
    Draw = 2,
    Show = 3
}

const showLoadOptionModal = ref<boolean>(false);
const imageUrlInput = ref<string>('');
const isLoading = ref<boolean>(false);
const imageBase64 = ref<string | null>(null);
const displayImgRef = ref<HTMLImageElement | null>(null);
const drawBoardRef = ref<InstanceType<typeof DrawRectCanvas> | null>(null);
const fullImageRef = ref<HTMLCanvasElement | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const status = ref<EditorStatus>(EditorStatus.Ready);
const editorSize = reactive<{width: number, height: number}>({width: 600, height: 450});

const syncCanvas = () => {
    if (displayImgRef.value) {
        editorSize.width = displayImgRef.value.width;
        editorSize.height = displayImgRef.value.height;
    }
    console.log(">>>do syncCanvas: " + editorSize.width + "," + editorSize.height);
}

const showModal = () => {
    showLoadOptionModal.value = true;
}

const closeModal = () => {
    showLoadOptionModal.value = false;
    imageUrlInput.value = '';
}

const triggerInput = () => {
    closeModal();
    fileInputRef.value?.click();
}

const handleFileChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
        console.log(">>> upload file: " + file.name);
        const reader = new FileReader();
        reader.onload = (e) => {
            imageBase64.value = e.target?.result as string;
            drawImage();
        };
        reader.readAsDataURL(file);
        status.value = EditorStatus.Edit;
    }
}

const loadImageFromUrl = async () => {
    if (!imageUrlInput.value) {
        alert('Please enter a valid URL');
        return;
    }

    isLoading.value = true;
    try {
        const response = await fetch(imageUrlInput.value);
        const blob = await response.blob();
        const reader = new FileReader();
        reader.onload = (e) => {
            imageBase64.value = e.target?.result as string;
            drawImage();
            status.value = EditorStatus.Edit;
            closeModal();
        };
        reader.readAsDataURL(blob);
    } catch (error) {
        console.error('Error loading image from URL:', error);
        alert('Failed to load image from URL');
    } finally {
        isLoading.value = false;
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
    if (drawBoardRef.value) {
        drawBoardRef.value.cancel();
    }
    if (fullImageRef.value) {
        const canvas = fullImageRef.value;
        const ctx = canvas.getContext('2d');
        ctx?.clearRect(0, 0, canvas.width, canvas.height);
    }
}

const rotateImage = () => {
    if (isLoading.value) return;

    if (fullImageRef.value === null) {
        return;
    }
    const canvas = fullImageRef.value;
    const ctx = canvas.getContext('2d');
    if (ctx === null) {
        return;
    }
    isLoading.value = true;
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
        isLoading.value = false;
    };
}

const clear = () => {
    drawBoardRef.value?.cancel();
}

const removebg = () => {
    if (isLoading.value) return;

    isLoading.value = true;
    const polygonPoints = drawBoardRef.value?.confirm() || [];
    const points: Array<Array<number>> = [];
    polygonPoints.forEach(point => {
        points.push([point.x, point.y]);
    });
    const payload = {
        base64: imageBase64.value,
        selectPolygon: points,
        editorSize: [editorSize.width, editorSize.height],
        responseFormat: 0
    };
    fetch('/removebg', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(resp => {
        if (resp.status == 200) {
            resp.json().then(apiResult => {
                if (apiResult.code != 0) {
                    alert(apiResult.msg);
                } else {
                    imageBase64.value = apiResult.result;
                    status.value = EditorStatus.Show;
                }
                isLoading.value = false;
            }).catch(error => {
                isLoading.value = false;
                console.log(error);
            });
        } else {
            isLoading.value = false;
            console.error(resp.status + ":" + resp.statusText);
        }
    })
    .catch(error => {
        isLoading.value = false;
        console.log(error);
    });
}

const stringToRandomNumber = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = (hash << 5) - hash + str.charCodeAt(i);
        hash |= 0;
    }
    const seed = Math.abs(hash);
    const random = (seed * 9301 + 49297) % 233280;
    return random / 233280;
}

const downloadPng = () => {
    if (imageBase64.value) {
        const link: HTMLAnchorElement = document.createElement('a');
        link.href = imageBase64.value;
        link.download = stringToRandomNumber(imageBase64.value) + '.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

const base64ToBlob = (base64: string) => {
    const byteString = atob(base64.split(',')[1]);
    const mimeString = base64.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

const sharePng = async () => {
    if (imageBase64.value) {
        const blob = base64ToBlob(imageBase64.value);
        const filesArray = [
            new File([blob], 'image.png', {
                type: blob.type,
            }),
        ];

        if (navigator.share) {
            try {
                await navigator.share({
                    files: filesArray,
                });
                console.log('分享成功');
            } catch (error) {
                console.error('分享失败', error);
            }
        } else {
            alert('Web Share API Not Supported');
        }
    }
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
.editor-container {
    flex: 1;
}

img {
    width: 600px;
    user-select: none;
    -webkit-user-drag: none;
}

.canvas-container {
    position: relative;
    width: 600px;
}

.iconfont {
    font-size: 48px;
    color: #18c064;
}

.button-container {
    top: 10px;
    left: 10px;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.button-container i {
    cursor: pointer;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 300px;
    text-align: center;
}

.url-input-container {
    display: flex;
    gap: 5px;
}

.url-input-container input {
    flex: 1;
    padding: 5px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

button {
    padding: 8px;
    border: none;
    background: #18c064;
    color: white;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background: #15a856;
}
</style>