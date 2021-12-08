<?php
$mode = $_POST['mode'];
$file = $_FILES['file'];
if (!is_dir('./files')) {
    mkdir('./files');
}
if (!file_exists('./counter.txt')){
    file_put_contents('./counter.txt', '0');
}
$id = (int)file_get_contents('./counter.txt');
file_put_contents('./counter.txt', (string)($id+1));
$path = "./files/{$id}__".basename($file['name']);
move_uploaded_file($file['tmp_name'], $path);
$result = json_decode((string)shell_exec(dirname(__file__)."/huffman.py -".($mode == 'compress' ? 'c' : 'd')." \"{$path}\""));
header('Content-Type: application/json');
echo json_encode($result);
?>