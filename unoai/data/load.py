# AUTOGENERATED! DO NOT EDIT! File to edit: dev/01_data.load.ipynb (unless otherwise specified).

__all__ = ['get_tf_example_from_raw_img', 'get_tf_example_from_numpy', 'store_np_imgs_as_tfrecord',
           'parse_tf_example_img', 'read_tfrecord_as_dataset']

# Cell
from ..imports import *

# Cell
def _bytes_feature(value) -> tf.train.Feature:
    "Returns a bytes_list from a string / byte."
    if isinstance(value, type(tf.constant(0))): value = value.numpy() # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _float_feature(value) -> tf.train.Feature:
    if not isinstance(value, list): value = [value]
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def _int64_feature(value) -> tf.train.Feature:
    "Returns an int64_list from a bool / enum / int / uint."
    if not isinstance(value, list): value = [value]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

def get_tf_example_from_raw_img(raw_img, y: None) -> tf.train.Example:
    if y is None: feat_dict = {'image': _bytes_feature(raw_img)}
    else:         feat_dict = {'image': _bytes_feature(raw_img), 'label': _int64_feature(y)}
    return tf.train.Example(features=tf.train.Features(feature=feat_dict))

def get_tf_example_from_numpy(x, y: None) -> tf.train.Example:
    if y is None: feat_dict = {'image': _float_feature(x.tolist())}
    else:         feat_dict = {'image': _float_feature(x.tolist()), 'label': _int64_feature(y)}
    return tf.train.Example(features=tf.train.Features(feature=feat_dict))

def store_np_imgs_as_tfrecord(output_path: str, x: np.array, y: np.array=None) -> None:
    n = x.shape[0]
    x_reshape = x.reshape(n,-1)
    with tf.io.TFRecordWriter(output_path) as w:
        for i in tqdm(range(n)):
            if y is None: ex = get_tf_example_from_numpy(x_reshape[i])
            else:         ex = get_tf_example_from_numpy(x_reshape[i], y[i])
            w.write(ex.SerializeToString())

def parse_tf_example_img(tf_example: tf.train.Example,h: int, w: int, c: int=3,dtype=tf.float32):
    feat_desc = {
        'image': tf.io.FixedLenFeature([h * w * c], dtype),
        'label': tf.io.FixedLenFeature([], tf.int64)
    }
    feat = tf.io.parse_single_example(tf_example,features=feat_desc)
    x, y = feat['image'], feat['label']
    x = tf.reshape(x, [h, w, c])
    return x, y

def read_tfrecord_as_dataset(ds_path: str, parser: Callable, batch_size: int = None,
                             shuffle: bool = True, shuffle_buffer_size: int = 50000,
                             prefetch: bool = False) -> tf.data.Dataset:
    ds = tf.data.TFRecordDataset(ds_path)
    if shuffle: ds = ds.shuffle(shuffle_buffer_size)
    ds = ds.map(parser, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    if batch_size is not None: ds = ds.batch(batch_size)
    if prefetch: ds = ds.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
    return ds