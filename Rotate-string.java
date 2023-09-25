import java.util.Scanner;

public class RotateString {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int t = scanner.nextInt();
        scanner.nextLine();  // Consume newline

        for (int i = 0; i < t; i++) {
            String s = scanner.nextLine();
            printRotations(s);
        }
    }

    public static void printRotations(String s) {
        for (int i = 1; i <= s.length(); i++) {
            System.out.print(s.substring(i) + s.substring(0, i) + " ");
        }
        System.out.println();
    }
}
