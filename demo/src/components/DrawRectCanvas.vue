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
    width: 800,
    height: 600
  })
  
  const canvasRef = ref<HTMLCanvasElement | null>(null);
  let startPoint: Point = {x:0, y:0}
  let endPoint: Point = {x:0, y:0}
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
    startPoint.x = Math.max(0, point.x)
    startPoint.y = Math.max(0, point.y)
  }
  
  const draw = (point: Point) => {
    if(!isDrawing) return;
    endPoint.x = Math.max(0, point.x)
    endPoint.y = Math.max(0, point.y)
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

    // 计算矩形的宽度和高度
    const width = Math.abs(endPoint.x - startPoint.x);
    const height = Math.abs(endPoint.y - startPoint.y);
    if(width == 0 || height == 0){
        return
    }

    // 计算矩形的左上角顶点
    const startX = Math.min(startPoint.x, endPoint.x);
    const startY = Math.min(startPoint.y, endPoint.y);
  
    // 设置虚线样式
    ctx.strokeStyle = "blue" 
    ctx.setLineDash([5, 5]); // 虚线样式，表示5像素实线和5像素空白
    ctx.lineWidth = 2; // 线条宽度

    // 绘制矩形
    ctx.beginPath();
    ctx.rect(startX, startY, width, height);
    ctx.stroke();
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
    const width = Math.abs(endPoint.x - startPoint.x);
    const height = Math.abs(endPoint.y - startPoint.y);
    const startX = Math.min(startPoint.x, endPoint.x);
    const startY = Math.min(startPoint.y, endPoint.y);
    return [{x:startX, y:startY}, {x:startX + width, y: startY}, {x:startX + width, y:startY + height}, {x:startX, y:startY+height}]
  };
  
  const cancel = () => {
      startPoint = {x:0, y:0}
      endPoint = {x:0, y:0}
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
  