export async function walkEntry(entry, path = "") {
  if (entry.isFile) {
    return new Promise((resolve) =>
      entry.file((file) => {
        file.fullPath = path + file.name;
        resolve([file]);
      })
    );
  }

  return new Promise((resolve) => {
    const dirReader = entry.createReader();
    const entries = [];
    const read = () =>
      dirReader.readEntries(async (batch) => {
        if (!batch.length) {
          const files = [];
          for (const child of entries) {
            files.push(...await walkEntry(child, path + entry.name + "/"));
          }
          resolve(files);
        } else {
          entries.push(...batch);
          read();
        }
      });
    read();
  });
}

export async function filesFromDataTransfer(dt) {
  const promises = [];
  for (const item of dt.items) {
    const entry = item.webkitGetAsEntry?.();
    if (entry) promises.push(walkEntry(entry));
  }
  const nested = await Promise.all(promises);
  return nested.flat();
}

export function setupDropZone(dropZoneId, onFilesReady) {
  const dropZone = document.getElementById(dropZoneId);

  ["dragenter", "dragover"].forEach((evt) =>
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.add("over");
    })
  );

  ["dragleave", "drop"].forEach((evt) =>
    dropZone.addEventListener(evt, () => dropZone.classList.remove("over"))
  );

  dropZone.addEventListener("drop", async (e) => {
    e.preventDefault();
    const droppedFiles = await filesFromDataTransfer(e.dataTransfer);
    onFilesReady(droppedFiles);
  });
}
