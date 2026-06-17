package routines;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class TalendDataGeneratorTest {

    @Test
    void firstNameNotEmpty() {
        String name = TalendDataGenerator.getFirstName();
        assertNotNull(name);
        assertFalse(name.isEmpty());
    }

    @Test
    void lastNameNotEmpty() {
        String name = TalendDataGenerator.getLastName();
        assertNotNull(name);
        assertFalse(name.isEmpty());
    }

    @Test
    void usStreetNotEmpty() {
        String street = TalendDataGenerator.getUsStreet();
        assertNotNull(street);
        assertFalse(street.isEmpty());
    }

    @Test
    void usStateNotEmpty() {
        String state = TalendDataGenerator.getUsState();
        assertNotNull(state);
        assertFalse(state.isEmpty());
    }

    @Test
    void usCityNotEmpty() {
        String city = TalendDataGenerator.getUsCity();
        assertNotNull(city);
        assertFalse(city.isEmpty());
    }
}
