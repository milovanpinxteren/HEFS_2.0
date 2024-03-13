
class FileComparer:
    def compare_files(self, file1, file2):
        print(file1, file2)
        differences = []
        data1 = {}
        try:
            with open(file1, 'r') as f:
                next(f)  # Skip header if present
                for line in f:
                    try:
                        barcode, stock = line.strip().split('\t')
                        data1[barcode] = int(stock)
                    except Exception as e:
                        barcode = line.strip()
                        data1[barcode] = 0

            # Read data from file2
            data2 = {}
            with open(file2, 'r') as f:
                next(f)  # Skip header if present
                for line in f:
                    try:
                        barcode, stock = line.strip().split('\t')
                        data2[barcode] = int(stock)
                    except Exception as e:
                        barcode = line.strip()
                        data1[barcode] = 0

            for barcode in data1:
                if barcode in data2:
                    if data1[barcode] != data2[barcode]:
                        differences.append((barcode, data2[barcode]))
                else:
                    differences.append((barcode, data1[barcode]))# Barcode only in file1

            for barcode in data2:
                if barcode not in data1:
                    differences.append((barcode, data2[barcode]))  # Barcode only in file2

            return differences
        except Exception as e:
            print('file_comparer error: ', e)
            return []