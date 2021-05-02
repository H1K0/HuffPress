<?php
$mode = $_POST['mode'];
$file = $_FILES['file'];
if (!is_dir(dirname(__file__) . '/files')) {
    mkdir(dirname(__file__) . '/files');
}
$path = dirname(__file__) . '/files/' . basename($file['name']);
move_uploaded_file($file['tmp_name'], $path);
$result = json_decode((string)shell_exec('python ' . dirname(__file__) . '/huffman.py -' . ($mode == 'compress' ? 'c' : 'd') . ' "' . $path . '"'));
header('Content-Type: application/json');
echo json_encode($result);
?>