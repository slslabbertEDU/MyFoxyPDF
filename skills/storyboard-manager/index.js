import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the current directory of this file
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function runPythonScript(scriptPath, argsArray) {
  return new Promise((resolve, reject) => {
    const process = spawn('python3', [scriptPath, ...argsArray]);

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Process exited with code ${code}. Stderr: ${stderr}`));
      } else {
        if (stderr && stderr.trim() !== '') {
          console.warn(`Warnings from script: ${stderr}`);
        }
        resolve(stdout);
      }
    });

    process.on('error', (err) => {
      reject(err);
    });
  });
}

export default async function storyboard_manager(input) {
  console.log("🧠 Running skill: storyboard-manager");
  
  try {
    let command = '';
    let targetDir = '.';
    let scriptArgs = [];

    // Handle different input formats
    if (typeof input === 'string') {
      // Very basic parsing for string input
      const text = input.toLowerCase();
      if (text.includes('timeline')) {
        command = 'timeline';
      } else if (text.includes('consistency')) {
        command = 'consistency';
      } else {
        return {
          success: true,
          message: "Storyboard Manager initialized. For character development, story planning, or chapter writing, please use standard file reading/writing tools as guided by the SKILL.md documentation. For automated checks, use the 'timeline' or 'consistency' commands.",
          input
        };
      }
    } else if (typeof input === 'object' && input !== null) {
      command = input.command || input.action || '';
      targetDir = input.targetDir || input.projectPath || '.';

      // if it's explicitly one of our commands, allow some extra args
      if (input.args && Array.isArray(input.args)) {
          scriptArgs = input.args;
      } else if (input.args && typeof input.args === 'string') {
          // split by spaces if a string is provided for args (though an array is preferred)
          scriptArgs = input.args.split(' ').filter(Boolean);
      }
    }

    if (!command) {
        // Fallback for LLMs sending general request text
        const text = JSON.stringify(input).toLowerCase();
        if (text.includes('timeline')) {
            command = 'timeline';
        } else if (text.includes('consistency')) {
            command = 'consistency';
        } else {
             return {
                success: true,
                message: "Storyboard Manager workflow started. Please use standard file operations to manage characters, plot, and chapters. Use commands 'timeline' or 'consistency' to run automated scripts.",
                input
             };
        }
    }

    // Resolve the python script paths
    const timelineScript = path.resolve(__dirname, 'scripts/timeline_tracker.py');
    const consistencyScript = path.resolve(__dirname, 'scripts/consistency_checker.py');

    let pythonScript = '';

    if (command === 'timeline' || command === 'timeline_tracker') {
      pythonScript = timelineScript;
    } else if (command === 'consistency' || command === 'consistency_checker') {
      pythonScript = consistencyScript;
    } else {
      return {
        success: true,
        message: `Command '${command}' not mapped to a Python script. Standard workflow initialized.`,
        input
      };
    }

    // Add targetDir as the first argument, followed by any additional args
    const finalArgs = [targetDir, ...scriptArgs];

    console.log(`Executing: python3 ${pythonScript} ${finalArgs.join(' ')}`);
    const stdout = await runPythonScript(pythonScript, finalArgs);

    return {
      success: true,
      message: `Skill 'storyboard-manager' executed '${command}' successfully!`,
      output: stdout,
      input
    };

  } catch (error) {
    console.error("Error executing storyboard-manager script:", error);
    return {
      success: false,
      message: `Error executing command: ${error.message}`,
      error: error.toString()
    };
  }
}
