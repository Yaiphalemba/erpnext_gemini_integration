<template>
  <div>
    <button 
      @click="toggleDrawer"
      class="fixed bottom-6 right-6 z-40 p-4 rounded-full bg-slate-800 text-orange-500 shadow-xl border border-white/10 hover:bg-slate-700 hover:scale-105 hover:shadow-orange-500/20 transition-all duration-300 group"
      title="Open AI Analyst (Cmd+K)"
    >
      <svg class="w-6 h-6 group-hover:animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    </button>

    <AIChatDrawer :isOpen="isOpen" @close="toggleDrawer" />
  </div>
</template>