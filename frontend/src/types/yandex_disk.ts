// Types for the Yandex Disk folder tree

export interface DiskFile {
    name: string;
    path: string;
    url: string;
}

export interface DiskFolder {
    name: string;
    path: string;
    folders: DiskFolder[];
    files: DiskFile[];
}
