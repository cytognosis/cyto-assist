/**
 * Cascade Configuration
 * 
 * Defines how the AI assistant interacts with the codebase.
 */

module.exports = {
  // Project Identity and Context
  project: {
    name: "cyto-assist",
    description: "Personal assistant and AI scientist project",
    domain: "Healthcare AI",
    stack: ["Python", "PyTorch", "Hatch", "Nox"],
  },

  // AI Behavior Preferences
  preferences: {
    // Coding Style
    codeStyle: "Google",
    useTypeHints: true,
    preferVectorized: true, // Prefer numpy/torch vectorization over loops

    // Safety & Compliance
    safetyCheck: true, // Prioritize safety in code generation
    phiAwareness: true, // Warn about PHI handling

    // Communication
    terse: false, // Be explanatory for scientific concepts
    language: "English",
  },

  // Custom Commands
  commands: {
    "test": "nox -s test",
    "lint": "nox -s lint",
    "format": "nox -s format",
    "docs": "nox -s docs_build",
    "init": "nox -s init_project",
  },

  // Shortcuts
  shortcuts: {
    "t": "test",
    "l": "lint",
    "f": "format",
  }
};
