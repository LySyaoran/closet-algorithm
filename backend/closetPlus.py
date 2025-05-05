import pandas as pd
import os
import json
import itertools
'''
    Cách itertools.combination(items, i) hoạt động: VD cho items = [A,B,C] và duyệt i từ [1;4)
        + itertools.combinations(items, 1) = (A,) (B,) (C,)
        + itertools.combinations(items, 2) = (A, B) (A, C) (B, C)
        + itertools.combinations(items, 3) = (A, B, C)
'''
from graphviz import Digraph  # biểu đồ để vẽ cây FP-tree
from itertools import combinations
from mlxtend.frequent_patterns import association_rules

'''
    suffix (tiền tố): VD: root --> b --> f với support là 2 ==> prefix itemset = {bf:2} 
    prefix (hậu tố): VD: root --> b --> f với support là 2 ==> suffix item = {f:2}
    -----> prefix = (tập phổ biến đã khai thác tại cây con) + (suffix)
'''

class FPNode(object):
    """
    A node in the FP tree.
    """
    def __init__(self, item, count, parent):
        """
        Create the node.
        """
        self.item = item
        self.count = count
        self.parent = parent
        self.link = None # dùng để liên kết tới node kế tiếp có cùng item (node cũ link node mới có cùng item) (dùng trong Header Table)
        self.children = []

    def has_child(self, item):
        """
        Check if node has a particular child node.
        """
        for node in self.children:
            if node.item == item:
                return True

        return False

    def get_child(self, item):
        """
        Return a child node with a particular item.
        """
        for node in self.children:
            if node.item == item:
                return node

        return None

    def add_child(self, item):
        """
        Add a node as a child node.
        """
        child = FPNode(item, 1, self) # item, count, parent
        self.children.append(child)
        return child


class FPTree(object):
    """
    A frequent pattern tree.
    """
    deletingClosedPatterns = {} # lưu các tập con phổ biến đóng cần xóa khi tìm thấy tập cha bao quát hơn tập con này
    def __init__(self, transactions, threshold, root_item, root_count, totalClosedPatterns: dict):
        """
        Initialize the tree.
        """
        self.frequent = self.find_frequent_items(transactions, threshold)
        self.headers = self.build_header_table(self.frequent)
        self.root = self.build_fptree(
            transactions, root_item,
            root_count, self.frequent, self.headers)
        self.closedPatterns = self.init_first_closed_item(root_item, root_count) # các tập phổ biến đóng tại prefix này
        self.totalClosedPatterns = totalClosedPatterns # lưu toàn bộ kết quả tập phổ biến đóng (mục đích: kiểm tra subset-prunning technique)


    '''#-----------------------------------------------Nơi để mà generate cho self.frequent, self.headers, build_fbtree với self.root là node root----------------------------------------------------------------------------------------------------'''
    @staticmethod
    def find_frequent_items(transactions, threshold):
        """
        Tìm các item thỏa ngưỡng minsup
        """
        items = {}
        
        # Đếm số support cho từng item, sao đó lưu vào items{}
        for transaction in transactions:
            for item in transaction:
                if item in items:
                    items[item] += 1
                else:
                    items[item] = 1
        
        # Loại các item có số support < minsup trong items{}
        for key in list(items.keys()):
            if items[key] < threshold:
                del items[key]

        return items

    @staticmethod
    def build_header_table(frequent):
        """
        Xây dựng header table
        """
        headers = {}
        for key in frequent.keys():
            headers[key] = None

        return headers

    def build_fptree(self, transactions, root_item,
                     root_count, frequent, headers):
        """
        Build the FP tree and return the root node.
        """
        root = FPNode(root_item, root_count, None)

        for transaction in transactions:
            # lọc transaction theo frequent
            sorted_items = [x for x in transaction if x in frequent]
            '''
                'reverse=true': sắp xếp giảm dần
                'reverse=false': sắp xếp tăng dần
                'key=lambda x': là một item trong sorted_items
                '(-frequent[x], x)': sắp xếp giảm dần theo số support trước, nếu số support bằng nhau thì sắp xếp theo bảng chữ cái
            '''
            sorted_items.sort(key=lambda x: (-frequent[x], x), reverse=False)

            if len(sorted_items) > 0:
                self.insert_tree(sorted_items, root, headers)

        return root
    
    def draw_fp_tree(self, node=None, dot=None):
        if node is None:
            node = self.root

        if dot is None:
            dot = Digraph()
            dot.node(str(id(node)), f"{node.item} : {node.count}")

        for child in node.children:
            dot.node(str(id(child)), f"{child.item} : {child.count}")
            dot.edge(str(id(node)), str(id(child)))
            self.draw_fp_tree(child, dot)

        return dot

    def insert_tree(self, items, node, headers):
        """
        Recursively grow FP tree.
        items = [C,W,A,T]
        node = root
        """
        first = items[0]
        child = node.get_child(first)
        if child is not None:
            child.count += 1
        else:
            # Add new child.
            child = node.add_child(first)

            # Link it to header structure. (link node con có cùng item trong header_table) (Dùng để khai thác tập phổ biến)
            if headers[first] is None:
                headers[first] = child
            else:
                current = headers[first] # headers[first] là một node
                while current.link is not None:
                    current = current.link
                current.link = child # node cũ link với node mới có cùng item

        # Call function recursively.
        remaining_items = items[1:]
        if len(remaining_items) > 0:
            self.insert_tree(remaining_items, child, headers)
    '''#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''



    '''#--------------------------------------------Nơi để khai thác tập phổ biến sau khi xây xong FP_tree-------------------------------------------------------------------------------------------------------'''
    def tree_has_single_path(self, node):
        """
        If there is a single path in the tree,
        return True, else return False.
        """
        num_children = len(node.children)
        if num_children > 1:
            return False
        elif num_children == 0:
            return True
        else: # num_children == 1
            return True and self.tree_has_single_path(node.children[0])

    def mine_patterns(self, threshold):
        """
        Mine the constructed FP tree for frequent patterns.
        """
        if self.tree_has_single_path(self.root):
            return self.generate_pattern_list()
        else:
            return self.zip_patterns(self.mine_sub_trees(threshold))

    def zip_patterns(self, patterns): # trường hợp vẫn còn đang trong FP-tree con
        """
        Append suffix to patterns in dictionary if
        we are in a conditional FP tree.
        (thêm prefix item vào patterns)
        """
        suffix = self.root.item

        if suffix is not None:
            # We are in a conditional tree.
            new_patterns = {}
            for key in patterns.keys():
                new_patterns[tuple(sorted(list(key) + [suffix]))] = patterns[key]

            return new_patterns

        return patterns

    def generate_pattern_list(self):
        """
        Generate a list of patterns with support counts.
        """
        patterns = {}
        items = self.frequent.keys()

        # If we are in a conditional tree,
        # the suffix is a pattern on its own.
        if self.root.item is None: # khi nó rơi vào trường hợp FP-tree cha có 1 nhánh duy nhất
            suffix_item = []
        else:
            suffix_item = [self.root.item]
            patterns[tuple(suffix_item)] = self.root.count

        for i in range(1, len(items) + 1):
            for subset in itertools.combinations(items, i):
                pattern = tuple(sorted(list(subset) + suffix_item))
                patterns[pattern] = \
                    min([self.frequent[x] for x in subset])

        return patterns

    def mine_sub_trees(self, threshold):
        """
        Generate subtrees and mine them for patterns.
        """
        patterns = {}
        mining_order = sorted(self.frequent.keys(),
                              key=lambda x: self.frequent[x])

        # Get items in tree in reverse order of occurrences.
        for item in mining_order:
            suffixes = [] # các node có cùng item
            conditional_tree_input = [] # support count thấp nhất của 1 nhánh (path)
            node = self.headers[item]

            # Follow node links to get a list of (đi theo các link của node có cùng item)
            # all occurrences of a certain item.
            while node is not None:
                suffixes.append(node)
                node = node.link

            # For each occurrence of the item, 
            # trace the path back to the root node. (duyệt từ node item đến node root)
            for suffix in suffixes:
                frequency = suffix.count # số support count tại node đó
                path = [] # các đường đi đến node root của item đang xét
                parent = suffix.parent

                while parent.parent is not None: # node C có parent là node root
                    path.append(parent.item)
                    parent = parent.parent

                for i in range(frequency):
                    conditional_tree_input.append(path)

            # Now we have the input for a subtree,
            # so construct it and grab the patterns. # Xây dựng FP-tree con tại prefix item đang xét
            subtree = FPTree(conditional_tree_input, threshold,
                             item, self.frequent[item], None)
            subtree_patterns = subtree.mine_patterns(threshold)

            # Insert subtree patterns into main patterns dictionary.
            for pattern in subtree_patterns.keys():
                if pattern in patterns:
                    patterns[pattern] += subtree_patterns[pattern] # cộng số support của patterns và subtree_patterns
                else:
                    patterns[pattern] = subtree_patterns[pattern]

        return patterns
    '''#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''



    '''#--------------------------------------------Nơi để khai thác tập phổ biến đóng sau khi xây xong FP_tree-------------------------------------------------------------------------------------------------------'''
    @staticmethod
    def init_first_closed_item(root_item, root_count):
        if root_item is None:
            return {}
        else:
            first_item_closed = {}
            first_item_closed[tuple([root_item])] = root_count
            return first_item_closed


    # Tìm đường đi từ node item đang xét đến suffix item
    def find_path_item(self, item):
        # ý tưởng dựa vào header_table để mà lấy node chính
        # sử dụng self.frequent nhưng sắp xếp tăng dần

        node = self.headers[item]
        suffixes = []
        conditional_tree_input = []
        
        while node is not None:
            suffixes.append(node)
            node = node.link

        # For each occurrence of the item, 
        # trace the path back to the root node. (duyệt từ node item đến node root)
        for suffix in suffixes:
            frequency = suffix.count # số support count tại node đó
            path = [] # các đường đi đến node root của item đang xét
            parent = suffix.parent

            while parent.parent is not None: # node C có parent là node root
                path.append(parent.item)
                parent = parent.parent

            for i in range(frequency):
                conditional_tree_input.append(path)
    
        return conditional_tree_input


    # Khai thác tập phổ biến đóng
    def mine_closedPatterns(self, threshold):
        """
        Mine the constructed FP tree for frequent patterns.
        """
        # if self.root.item is None:
        #     totalClosedPatterns.clear()
        if self.tree_has_single_path(self.root):
            return self.generate_closedPattern_list()
        else:
            return self.zip_closedPatterns(self.mineClosed_sub_trees(threshold))


    # Gộp suffix item vào các tập phổ biến đóng đã khai thác được
    def zip_closedPatterns(self, patterns): 
        """
        Append suffix to patterns in dictionary if
        we are in a conditional FP tree.
        (thêm prefix item vào patterns)
        """
        
        suffix = self.root.item

        # trường hợp vẫn còn đang trong FP-tree con --> tiến hành gộp suffix item với các tập phố biến đóng đã khai thác
        if suffix is not None:
            # We are in a conditional tree.
            new_patterns = {}
            for key in patterns.keys():
                if set([suffix]).issuperset(set(key)): # nếu suffix item cũng chính là tập phổ biến đóng chứa trong patterns thì bỏ qua, tránh trùng lặp khi gộp
                    new_patterns[tuple(key)] = patterns[key]
                else:
                    new_patterns[tuple(sorted(list(key) + [suffix]))] = patterns[key]

            return new_patterns

        # Trường hợp đây là cây cha thì trả về kết quả đã khai thác được tất cả tập phổ biến đóng
        return patterns
    

    '''
        # Nếu là cây có 1 nhánh thì bắt đầu tìm các tập phổ biến đóng sử dụng 3 kỹ thuật
        # Kỹ thuật 1: item_skipping --> kiểm tra xem suffix item có phải là con của tập phổ biến đóng có cùng số support không. Có thì cắt tỉa (không cần xét nữa)
        # Kỹ thuật 2: subset_prunning --> kiểm tra xem prefix itemset có phải là con của tập phổ biến đóng có cùng số support không. Có thì cắt tỉa (không cần xét nữa)
        # Kỹ thuật 3: item_merging --> kết hợp prefix itemset với itemset không chứ prefix itemset với điều kiện là cùng support với prefix itemset. Nếu kết hợp được trả về kết quả 'gộp itemset' là tập phổ biến đóng mới
        # Trường hợp mà không rơi vào kỹ thuật gì hết thì trả về kết quả với prefix itemset là tập phổ biến đóng mới.
    '''
    def generate_closedPattern_list(self):
        """
        Generate a list of patterns with support counts.
        """
        # Kỹ thuật 1: bỏ qua item (item_skipping)
        if self.item_skipping():
            return self.closedPatterns
        else:
            suffix_item = self.root.item #if self.root.item is not None else ''
            mining_order = sorted(self.frequent.keys(),
                              key=lambda x: self.frequent[x])

            for item in mining_order:
                # suffix_item + item --> prefix_item
                if suffix_item is not None:
                    prefix_item = tuple(sorted([suffix_item] + [item]))
                else:
                    prefix_item = tuple(sorted([item]))
                prefix_count = self.frequent[item]

                # Kỹ thuật 2: cắt tỉa tập con (subset-prunning technique)
                if self.subset_prunning(prefix_item, prefix_count, self.totalClosedPatterns) == False: # trả về true/false
                    # Tìm đường đi của item trong bảng header_table đến node prefix
                    conditional_tree_input = self.find_path_item(item)

                    # Kỹ thuật 3: kết hợp item (item merging technique)
                    merged_itemset = self.item_merging(conditional_tree_input, prefix_item, prefix_count)
                    if merged_itemset is not None:
                        self.closedPatterns.update(merged_itemset)
                    
                    # trường hợp mà nó không thỏa 3 kỹ thuật trên thì thêm tập phổ biến đóng mới tại suffix item này
                    else:
                        if suffix_item is not None:
                            if self.root.count == prefix_count:
                                del self.closedPatterns[tuple([suffix_item])]
                        new_pattern = {}
                        new_pattern[prefix_item] = prefix_count
                        self.closedPatterns.update(new_pattern)
                else:
                    pass
            
        return self.closedPatterns


    # Kỹ thuật 3: item_merging --> kết hợp prefix itemset với itemset không chứ prefix itemset với điều kiện là cùng support với prefix itemset. Nếu kết hợp được trả về kết quả 'gộp itemset' là tập phổ biến đóng mới
    def item_merging(self, projected_transaction, prefix_item, prefix_count):
        merged_itemset = {}

        # Nếu không có transaction nào hết thì trả về None
        if not projected_transaction:
            return None

        # Đếm từng item riêng lẻ vào tạo bảng gồm item và count --> frequent_table
        frequent_table = {}
        for itemset in projected_transaction:
            for item in itemset:
                # counter[item] += 1
                if item in frequent_table:
                    frequent_table[item] += 1
                else:
                    frequent_table[item] = 1
        
        # Lọc các item có cùng support với prefix_item
        common_items = [item for item, count in frequent_table.items() if count == prefix_count]
        if not common_items:
            return None

        # gộp prefix item với các item cùng support với nó
        new_itemset = tuple(sorted(list(prefix_item) + list(common_items)))

        # Kiểm tra xem tập đóng mới này có phải là tập cha của một tập phổ biến đóng trong tập vừa mới khai thác gần đây không?
        # lưu ý: xét trên prefix/suffix đang khai thác
        for itemset, count in self.closedPatterns.items():
            if set(new_itemset).issuperset(set(itemset)) and prefix_count == count:
                del self.closedPatterns[itemset]
                break

        merged_itemset[new_itemset] = prefix_count
        
        # Kiểm tra xem tập đóng mới này có phải là tập cha của một tập phổ biến đóng trong toàn bộ tập đã khai thác xong không?
        # lưu ý: xét trên toàn bộ tập phổ biến đóng đã khai thác
        for itemset, count in self.totalClosedPatterns.items():
            if set(new_itemset).issuperset(set(itemset)) and prefix_count == count:
                self.deletingClosedPatterns[itemset] = count
                break

        return merged_itemset


    # Kỹ thuật 2: subset_prunning --> kiểm tra xem prefix itemset có phải là con của tập phổ biến đóng có cùng số support không. Có thì trả về True
    def subset_prunning(self, prefix_itemset, prefix_count, totalClosedPatterns: dict):
        # kiểm tra sự cắt tỉa thông qua tập phổ biến đóng vừa mới khai thác được tại prefix item này
        for itemset, count in self.closedPatterns.items():
            if set(prefix_itemset).issubset(set(itemset)) and prefix_count == count:
                return True
        # kiểm tra sự cắt tỉa thông qua tập phổ biến đóng đã khai thác được toàn bộ
        for itemset, count in totalClosedPatterns.items():
            if set(prefix_itemset).issubset(set(itemset)) and prefix_count == count:
                return True
            
        return False


    # Kỹ thuật 1: item_skipping --> kiểm tra xem suffix item có phải là con của tập phổ biến đóng có cùng số support không. Có thì cắt tỉa (không cần xét nữa)
    def item_skipping(self):
        # trường hợp mà frequent rỗng thì return cũng như thêm tập phổ biến đóng là suffix item (node root)
        if not self.frequent:
            new_pattern = {}
            new_pattern[tuple([self.root.item])] = self.root.count
            self.closedPatterns.update(new_pattern)
            return True
        else:
            prefix_item = self.root.item
            prefix_count = self.root.count
            for itemset, count in self.totalClosedPatterns.items():
                if set(prefix_item).issubset(set(itemset)) and prefix_count == count:
                    return True
                
        return False


    # Khai thác tập phổ biến đóng từ FP-tree con
    def mineClosed_sub_trees(self, threshold):
        """
        Generate subtrees and mine them for patterns.
        """
        mining_order = sorted(self.frequent.keys(),
                              key=lambda x: self.frequent[x])

        # Get items in tree in reverse order of occurrences.
        for item in mining_order:
            suffixes = [] # các node có cùng item
            conditional_tree_input = [] # transactions con với item đóng vai trò là node root --> suffix
            node = self.headers[item]

            # Follow node links to get a list of (đi theo các link của node có cùng item)
            # all occurrences of a certain item.
            while node is not None:
                suffixes.append(node)
                node = node.link

            # For each occurrence of the item, 
            # trace the path back to the root node. (duyệt từ node item đến node root)
            for suffix in suffixes:
                frequency = suffix.count # số support count tại node đó (suffix)
                path = [] # đường đi từ node đang xét (suffix) đến node root của item đang xét
                parent = suffix.parent

                while parent.parent is not None: # node C có parent là node root
                    path.append(parent.item)
                    parent = parent.parent

                for i in range(frequency):
                    conditional_tree_input.append(path)

            # Now we have the input for a subtree,
            # so construct it and grab the patterns. # Xây dựng FP-tree con tại prefix item đang xét
            subtree = FPTree(conditional_tree_input, threshold,
                             item, self.frequent[item], self.totalClosedPatterns)
            subtree_closedPatterns = subtree.mine_closedPatterns(threshold)
            
            # Cập nhật các tập phổ biến đóng đã khai thác được từ FP-tree con
            self.update_closedPatterns_and_totalClosedPatterns(subtree_closedPatterns)

            # # Insert subtree patterns into main patterns dictionary.
            # for pattern in subtree_closedPatterns.keys():
            #     if pattern in closedPatterns:
            #         closedPatterns[pattern] += subtree_closedPatterns[pattern]
            #     else:
            #         closedPatterns[pattern] = subtree_closedPatterns[pattern]

        return self.closedPatterns
    

    # Cập nhật các tập phổ biến đóng đã khai thác được từ FP-tree con
    def update_closedPatterns_and_totalClosedPatterns(self, subtree_closedPatterns: dict):
        self.closedPatterns.update(subtree_closedPatterns)
        self.totalClosedPatterns.update(subtree_closedPatterns)
        for itemset, _ in self.deletingClosedPatterns.items():
            if itemset in self.closedPatterns:
                del self.closedPatterns[itemset]
                del self.totalClosedPatterns[itemset]
        self.deletingClosedPatterns.clear() # sau khi xóa xong thì clear đi
    '''#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''



# Khai thác tập phổ biến
def find_frequent_patterns(transactions, support_threshold):
    """
    Given a set of transactions, find the patterns in it
    over the specified support threshold.
    """
    min_supCount = int(len(transactions) * support_threshold) # lấy số support count
    tree = FPTree(transactions, min_supCount, None, None, None)
    patterns = tree.mine_patterns(min_supCount)

    # Nếu dữ liệu rỗng thì return None
    if not patterns:
        return None, tree
    return patterns, tree

# Khai thác tập phổ biến đóng (dạng bottom-up physical tree-projection)
def find_closedFrequent_patterns_bottomUp(transactions, support_threshold):
    """
    Given a set of transactions, find the patterns in it
    over the specified support threshold.
    """
    min_supCount = int(len(transactions) * support_threshold) # lấy số support count
    tree = FPTree(transactions, min_supCount, None, None, {})
    closed_patterns = tree.mine_closedPatterns(min_supCount)

    # Nếu dữ liệu rỗng thì return None
    if any(None in key for key in closed_patterns):
        return None, tree
    return closed_patterns, tree


#-------------------------------------- Khai thác luật --------------------------------------------
# Tính support theo transactions
def calculate_support(itemset, transactions):
    count = sum(1 for t in transactions if itemset.issubset(t))
    return count / len(transactions)

# Mở rộng tất cả tập con từ frequent_itemsets_dict
def expand_frequent_itemsets(frequent_itemsets_dict):
    expanded = {}
    for itemset, count in frequent_itemsets_dict.items():
        itemset = set(itemset)
        for i in range(1, len(itemset)+1):
            for subset in combinations(itemset, i):
                subset_fs = frozenset(subset)
                if subset_fs not in expanded:
                    expanded[subset_fs] = count
                else:
                    expanded[subset_fs] = max(expanded[subset_fs], count)
    return expanded

# Hàm chính
def generate_association_rules(transactions: list, frequent_itemsets_dict: dict, min_confidence: float):
    # Bước 1: Mở rộng tập con
    expanded_dict = expand_frequent_itemsets(frequent_itemsets_dict)

    # Bước 2: Tính support từ transactions cho đúng
    df_freq = pd.DataFrame([
        {'itemsets': frozenset(k), 'support': calculate_support(set(k), transactions)}
        for k in expanded_dict.keys()
    ])

    # Bước 3: Sinh luật bằng mlxtend
    rules_df = association_rules(df_freq, metric="confidence", min_threshold=min_confidence)

    # Bước 4: Định dạng kết quả
    formatted_rules = []
    for _, row in rules_df.iterrows():
        antecedent = ', '.join(sorted(row['antecedents']))
        consequent = ', '.join(sorted(row['consequents']))
        rule_str = f"{antecedent} => {consequent}"
        formatted_rules.append({
            'Rule': rule_str,
            'Support': round(row['support'], 3),
            'Confidence': round(row['confidence'], 3),
            'Lift': round(row['lift'], 3)
        })

    return formatted_rules
#--------------------------------------------------------------------------------------------------------


# Xử lý chuyển đổi dữ liệu file csv thành dữ liệu có 2 thuộc tính: TID và Items
# --> Lưu vào file với tên file là 'new_file_name.csv' sau khi xử lý xong
def data_preprocessing(file_path: str, new_file_name: str):
    # đọc file_path.csv
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Lỗi: Không tìm thấy tệp tại {file_path}")
    except Exception as e:
        raise Exception(f"Lỗi khi đọc tệp: {e}")
    
    # # Xóa cột 'Unnamed: 0' nếu không chứa thông tin cần thiết
    # df = df.drop(columns=['Unnamed: 0'])
    # if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

    transactions = []
    # lấy các items có true trong mỗi dòng
    for _, row in df.iterrows():
        items = row[row == True].index.tolist()
        transactions.append(items)

    df_transactions = pd.DataFrame({
        'TID': range(1, len(transactions) + 1),
        'Items': [",".join(items) for items in transactions]
    })
    # lưu file csv mới vào thư mục hiện tại với tên là {new_file_name}.csv
    df_transactions.to_csv(f"{new_file_name}.csv", index=False)

    # # Đọc 10 dòng đầu tiên
    # return df_transactions.head(10)

    # Đọc hết
    return df_transactions

# Lấy dữ liệu đã được xử lý từ file csv và thêm vào transactions
def getDataProcessed_csv(file_path: str):
    # Lấy tên gốc của file, ví dụ: 'a.csv' -> 'a'
    base_name = os.path.basename(file_path)
    name_only, _ = os.path.splitext(base_name)

    # Tạo tên file mới và thư mục lưu trữ
    processed_folder = 'processed'
    os.makedirs(processed_folder, exist_ok=True)

    new_file_name = f"{name_only}_processed"
    full_processed_path = os.path.join(processed_folder, f"{new_file_name}.csv")

    # Gọi hàm tiền xử lý và lưu kết quả vào file mới
    data_preprocessing(file_path=file_path, new_file_name=os.path.join(processed_folder, new_file_name))

    # Đọc file đã chuẩn hóa
    try:
        data = pd.read_csv(full_processed_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Lỗi: Không tìm thấy tệp tại {full_processed_path}")
    except Exception as e:
        raise Exception(f"Lỗi khi đọc tệp: {e}")

    # Tạo danh sách transactions
    transactions = data['Items'].apply(lambda x: x.split(','))
    transactions = transactions.tolist()
    return transactions