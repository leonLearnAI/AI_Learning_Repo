if __name__ == '__main__':
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    iris =load_iris()
    print(iris.target_names)
    print(iris.target)
    
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)
    print("X_train shape:", X_train.shape)
    print('y_train count', len(y_train))
    print('x_test shape:', X_test.shape)
    print('y_test count:', len(y_test))