import React from "react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";

export default function SettingsPage({ onBack, onRestart }) {
  return (
    <div className="w-full h-full bg-gray-900 bg-opacity-80 flex items-center justify-center p-6">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-xl flex flex-col gap-6 w-96 text-center">
        <h1 className="text-3xl font-bold text-white">Settings</h1>

        <div className="flex flex-col gap-4 text-left">
          <label className="text-white text-lg font-semibold">Volume</label>
          <Slider defaultValue={[50]} max={100} step={1} className="w-full" />
        </div>

        <Button onClick={onRestart} className="w-full text-lg py-3 rounded-2xl shadow-md bg-red-600 hover:bg-red-700">
          Restart Game
        </Button>

        <Button onClick={onBack} className="w-full text-lg py-3 rounded-2xl shadow-md">
          Back
        </Button>
      </div>
    </div>
  );
}
