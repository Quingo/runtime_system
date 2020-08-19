import qgrtsys.core.data_transfer as dt
import pathlib


def test_read_long_bool_arr():
    cur_dir = pathlib.Path(__file__).parent.absolute()

    data_dir = cur_dir / 'data'
    bool_arr_fn = data_dir / 'res_gen_ran_seq.bin'

    data_trans = dt.Data_transfer()

    with open(bool_arr_fn, 'rb') as bin_file:
        result = bin_file.read()

        data_trans.set_data_block(result)

        ret_type = 'bool[]'

        res = data_trans.bin_to_pydata(ret_type, start_addr=0)
        assert(len(res) == 10000)


if __name__ == '__main__':
    test_read_long_bool_arr()
