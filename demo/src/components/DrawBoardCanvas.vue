<template>
  <canvas
    ref="canvasRef"
    style="position: absolute; top: 0; left: 0;"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
    @mousedown="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @mouseleave="handleMouseLeave"
    :width="width"
    :height="height"
  ></canvas>  
</template>

<script lang="ts" setup>
import { ref } from 'vue';

interface IProp {
  width: number,
  height: number
}

interface Point {
  x: number,
  y: number,
}

withDefaults(defineProps<IProp>(), {
  width: 700,
  height: 500
})

const canvasRef = ref<HTMLCanvasElement | null>(null);
let polygonPoints: Array<Point> = [];
let isDrawing = false;

const getCanvasCoordinates = (clientX: number, clientY: number):Point => {
  if (canvasRef.value == null) return { x: 0, y: 0 };
  const rect = canvasRef.value.getBoundingClientRect();
  return {
    x: clientX - rect.left,
    y: clientY - rect.top
  };
}

const startDrawing = (point: Point) => {
  isDrawing = true;
  polygonPoints.push(point)
}

const draw = (point: Point) => {
  if(!isDrawing) return;
  polygonPoints.push(point)
  redrawCanvas()
}

const stopDrawing = () => {
  isDrawing = false;
}

const redrawCanvas = () => {
  if(canvasRef.value == null) return;
  const ctx = canvasRef.value.getContext('2d')
  if(ctx == null) return;
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);

  if(polygonPoints.length < 2) return;

  // 设置虚线样式
  ctx.strokeStyle = "blue" 
  ctx.setLineDash([5, 5]); // 虚线样式，表示5像素实线和5像素空白
  ctx.lineWidth = 2; // 线条宽度
  
  ctx.beginPath();
  ctx.moveTo(polygonPoints[0].x, polygonPoints[0].y);
  polygonPoints.forEach(point => ctx.lineTo(point.x, point.y));
  ctx.stroke();  
}

const closePolygon = () => {
  if(polygonPoints.length > 2 && canvasRef.value != null){
    const ctx = canvasRef.value.getContext('2d')
    if(ctx == null) return;
    ctx.lineTo(polygonPoints[0].x, polygonPoints[0].y);
    ctx.stroke();
    console.log("Polygon closed. Points:", polygonPoints);
    isDrawing = false; // 阻止继续绘制
  }
}

const handleTouchStart = (event: TouchEvent) => {
  const touch = event.touches[0]
  draw(getCanvasCoordinates(touch.clientX, touch.clientY))
  event.preventDefault()
}

const handleTouchEnd = (event: TouchEvent) => {
  stopDrawing()
}

const handleMouseDown = (event: MouseEvent) => {
  startDrawing(getCanvasCoordinates(event.clientX, event.clientY))
}

const handleMouseMove = (event: MouseEvent) => {
  if(isDrawing){
    draw(getCanvasCoordinates(event.clientX, event.clientY))
  }
}

const handleMouseUp = (event: MouseEvent) => {
  stopDrawing()
}

const handleMouseLeave = (event: MouseEvent) => {
  stopDrawing()
}

const confirm = ():Array<Point> => {
  closePolygon()
  return polygonPoints
};

const cancel = () => {
    polygonPoints = []
    redrawCanvas()
};


defineExpose({ confirm, cancel });
</script>

<style>
.canvas-container{
  position: absolute;
  left: 0;
  top: 0;
}
canvas {
  touch-action: none; /* 禁用触摸操作的默认行为 */
}
</style>
