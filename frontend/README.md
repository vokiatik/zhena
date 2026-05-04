# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

i need u to update the process of uploading file. 

when file has been uploaded code need to check if there is any settings in process settings according to this exact process (with the tag file upload). Then if so i need it to check if there is attribute settings. If so i need to verify if all the values from the file in the column specifyed in attribute settings are already saved in the database in the reference table with a specific reference type. If so just continue. I need to do that for all the columns specifyied in the settings. then If not all the values are presented i need a func to return a list of all the values which are not in the db with corresponding type and then send a response to frontend that there have been added new values. 

on the frontend i need a modal being showed with a text like there have been found new dict values. and i need frontend to show this list in a modal that are not hiding untill user reacts. 

a need a table with 4 columns first column is a type_name and also i need to paint table to different background colors according to the values in that field. next column is a value that could be added. next i need a checkbox which is default as true meaning that this value will be saved. and the last column is an empty dropdown with values from reference table with exact type. Default is none. If iuts being changed to non null value corresponding checkbox is false. if it is none checkbox is true. And i need 2 buttons with different actions. One is save and proceed other is don't save and stop. first one need to send the data that user has chosen. Also if there is more than 20 rows in the table i need to add a frontend paggination.

first one sends a request to the backend that data has to be saved and file should be proceeded. So then i need a function to save this values according to their types and also one func that changes choosen values in the columns to the new ones. And then file being proceeded. 

if stop button was pressed i need to stop the file uploading function. 

so i need to update statuses of file processing as well. so file could be on hold intill user decides what to do with all the new values. 