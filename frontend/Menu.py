import React from "react";
import { Button } from "@/components/ui/button";

export default function MenusPage({ onResume, onSaveQuit, onSettings }) {
  return (
    <div className="w-full h-full bg-gray-900 bg-opacity-80 flex items-center justify-center p-6">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-xl flex flex-col gap-6 w-96 text-center">
        <h1 className="text-3xl font-bold text-white">Paused</h1>

        <Button onClick={onResume} className="w-full text-lg py-3 rounded-2xl shadow-md">
          Resume Game
        </Button>

        <Button onClick={onSaveQuit} className="w-full text-lg py-3 rounded-2xl shadow-md">
          Save & Quit to Title
        </Button>

        <Button onClick={onSettings} className="w-full text-lg py-3 rounded-2xl shadow-md">
          Settings
        </Button>
      </div>
    </div>
  );
}
