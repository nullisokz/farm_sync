
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import joblib, os

def main():
    os.makedirs("models", exist_ok=True)

    print("[1/5] Laddar MNIST…")
    
    mnist = fetch_openml("mnist_784", version=1, cache=True, as_frame=False)
    X = mnist["data"][:70000]
    y = mnist["target"][:70000].astype(np.uint8)

    print("[2/5] Train/val/test split…")
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.20, random_state=42, stratify=y_train_val
    )

    print("[3/5] Scaling features…")
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    print("[4/5] Training ExtraTrees…")
    clf = ExtraTreesClassifier(
        n_estimators=200,           
        max_depth=None,
        n_jobs=-1,
        random_state=42
    )
    clf.fit(X_train_s, y_train)

    val_acc = accuracy_score(y_val, clf.predict(X_val_s))
    print(f"Val-accuracy: {val_acc:.4f}")

    test_acc = accuracy_score(y_test, clf.predict(X_test_s))
    print(f"Test-accuracy: {test_acc:.4f}")
    print("\nClassification report (test):")
    print(classification_report(y_test, clf.predict(X_test_s)))

    print("[5/5] Sparar modell och scaler…")
    joblib.dump(clf, "models/mnist_et.joblib")
    joblib.dump(scaler, "models/mnist_scaler.joblib")
    print("✅ Saved: models/mnist_et.joblib, models/mnist_scaler.joblib")

if __name__ == "__main__":
    main()
